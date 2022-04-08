from smtplib import SMTPException

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse
from django.shortcuts import render

from vote.models import POLL_TYPES, Poll, Choice, Token


def create(request):
    def parse_mails(mails):
        result = []
        for mail in mails.split("\n"):
            mail = mail.strip()
            if not mail:
                continue
            if mail.count("@") != 1 or mail.split("@")[1].count(".") == 0:
                raise ValidationError("Mail %s invalid" % mail)
            result.append(mail)
        return result

    def parse_choices(choices):
        result = []
        for choice in choices.split("\n"):
            choice = choice.strip()
            if not choice:
                continue
            result.append(choice)
        return result

    def create_choice_objects(choices, poll):
        result = []
        for choice in choices:
            choice_obj = Choice(poll=poll, choice_text=choice)
            choice_obj.save()
            result.append(choice_obj)
        return result

    def create_token_objects(poll, amount):
        result = []
        for i in range(amount):
            token = Token(poll=poll)
            token.save()
            result.append(token)
        return result

    def send_mail_or_print(args, print_only=False):
        if print_only:
            print(*args)
        else:
            send_mail(*args, fail_silently=False)

    def send_creator_mail(poll, creator_mail, creator_token, print_only=False):
        manage_url = settings.VOTE_BASE_URL + reverse('vote:polls:manage', args=(poll.identifier,))
        args = (settings.VOTE_ADMIN_MAIL_SUBJECT % {"title": poll.title},
                settings.VOTE_ADMIN_MAIL_TEXT % {
                    "title": poll.title, "manage_url": manage_url, "creator_token": creator_token
                },
                settings.VOTE_MAIL_FROM,
                [creator_mail],
                )
        send_mail_or_print(args, print_only)

    def send_mails_with_tokens(poll, voter_mails, tokens, print_only=False):
        token_strings = [token.token_string for token in tokens]
        errors = []
        for voter_mail in voter_mails:
            poll_url_with_token = settings.VOTE_BASE_URL + reverse('vote:polls:poll', args=(
                poll.identifier,)) + '?token=' + token_strings.pop()
            args = (settings.VOTE_MAIL_SUBJECT % {"title": poll.title},
                    settings.VOTE_MAIL_TEXT % {
                        "title": poll.title,
                        "poll_url_with_token": poll_url_with_token,
                        "vote_base_url": settings.VOTE_BASE_URL
                    },
                    settings.VOTE_MAIL_FROM,
                    [voter_mail],
                    )
            try:
                send_mail_or_print(args, print_only)
            except SMTPException as e:
                errors.append(str(e))
            except UnicodeEncodeError as e:
                errors.append("%s " % voter_mail + str(e))
        return errors

    p_title = request.POST['title']
    p_type = request.POST['type']
    if p_type not in POLL_TYPES:
        raise Exception('Invalid poll type')
    p_description = request.POST['description']
    creator_mail = request.POST['creator_mail']
    voter_mails = request.POST['voter_mails']
    choices = request.POST['choices']
    voter_mails = parse_mails(voter_mails)
    choices = parse_choices(choices)
    poll = Poll(title=p_title, type=p_type, num_tokens=len(voter_mails), question_text=p_description)
    poll.save()
    choice_objects = create_choice_objects(choices, poll)
    tokens = create_token_objects(poll, len(voter_mails))
    send_creator_mail(poll, creator_mail, poll.creator_token, not settings.VOTE_SEND_MAILS)
    errors = send_mails_with_tokens(poll, voter_mails, tokens, not settings.VOTE_SEND_MAILS)
    context = {
        "errors": errors
    }
    return render(request, 'vote/create.html', context)
