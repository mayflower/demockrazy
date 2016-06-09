from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404

from .models import Poll, Choice, Token

def poll(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    token = request.GET.get('token', "Please enter your voting token")
    amount_redeemed_tokens, amount_remaining_tokens, amount_tokens_total = poll.get_amount_used_unused()
    if poll.is_active:
        return render(request, 'vote/poll.html', {'poll': poll, 'token': token, "amount_redeemed_tokens": amount_redeemed_tokens, "amount_remaining_tokens": amount_remaining_tokens, "amount_tokens_total": amount_tokens_total })
    else:
        return HttpResponseRedirect(reverse('vote:result', args=(poll_identifier,)))


def index(request):
    return render(request, 'vote/index.html')


def create(request):
    def parse_mails(mails):
        result  = []
        for mail in mails.split("\n"):
            mail  = mail.strip()
            if not mail:
                continue
            if mail.count("@") != 1 or mail.split("@")[1].count(".") == 0:
                raise ValidationError("Mail %s invalid" % mail)
            result.append(mail)
        return result
    def parse_choices(choices):
        result  = []
        for choice in choices.split("\n"):
            choice  = choice.strip()
            if not choice:
                continue
            result.append(choice)
        return result
    def create_choice_objects(choices, poll):
        result  = []
        for choice in choices:
            choice_obj  = Choice(poll = poll, choice_text = choice)
            choice_obj.save()
            result.append(choice_obj)
        return result
    def create_token_objects(poll, amount):
        result  = []
        for i in range(amount):
            token = Token(poll=poll)
            token.save()
            result.append(token)
        return result
    def send_creator_mail(poll, creator_mail, creator_token):
        manage_url = settings.VOTE_BASE_URL + reverse('vote:manage', args=(poll.identifier,))
        send_mail('demockrazy: You created a new poll',
                  "Hi, you just created a new poll that is manageable at %(manage_url)s\nYour admin token is: %(creator_token)s\nThank you for flying with LuftHansa" % { "manage_url": manage_url, "creator_token": creator_token},
            settings.VOTE_MAIL_FROM,
            [creator_mail],
            fail_silently=False,
        )
    def send_mails_with_tokens(poll, voter_mails, tokens):
        token_strings = [token.token_string for token in tokens]
        for voter_mail in voter_mails:
            poll_url_with_token = settings.VOTE_BASE_URL + reverse('vote:poll', args=(poll.identifier,)) + '?token=' + token_strings.pop()
            send_mail(settings.VOTE_MAIL_SUBJECT,
                settings.VOTE_MAIL_TEXT % { "poll_url_with_token": poll_url_with_token, "vote_base_url": settings.VOTE_BASE_URL},
                settings.VOTE_MAIL_FROM,
                [voter_mail],
                fail_silently=False,
            )
    p_title = request.POST['title']
    p_description = request.POST['description']
    creator_mail  = request.POST['creator_mail']
    voter_mails = request.POST['voter_mails']
    choices = request.POST['choices']
    voter_mails = parse_mails(voter_mails)
    choices = parse_choices(choices)
    poll = Poll(title=p_title, question_text=p_description)
    poll.save()
    choice_objects  = create_choice_objects(choices, poll)
    tokens   = create_token_objects(poll, len(voter_mails))
    send_creator_mail(poll, creator_mail, poll.creator_token)
    send_mails_with_tokens(poll, voter_mails, tokens)
    return render(request, 'vote/create.html')


def vote(request, poll_identifier):
    def handle_vote_error(poll, request, message, token_string):
        amount_redeemed_tokens, amount_remaining_tokens, amount_tokens_total = poll.get_amount_used_unused()
        return render(request, 'vote/poll.html', {
            'poll': poll,
            'error_message': message,
            'token': token_string,
            "amount_redeemed_tokens": amount_redeemed_tokens,
            "amount_remaining_tokens": amount_remaining_tokens,
            "amount_tokens_total": amount_tokens_total
        })

    poll = get_object_or_404(Poll, identifier=poll_identifier)
    if not poll.is_active:
        return HttpResponseRedirect(reverse('vote:result', args=(poll_identifier,)))
    try:
        token_string = request.POST['token']
        token = Token.objects.get(token_string=request.POST['token'])
        selected_choice = poll.choice_set.get(pk=request.POST['choice'])
    except KeyError:
        return handle_vote_error(poll, request, "Please fill out all fields.", token_string)
    except Choice.DoesNotExist:
        return handle_vote_error(poll, request, "You didn't select a choice.", token_string)
    except Token.DoesNotExist:
        return handle_vote_error(poll, request, "invalid token.", token_string)
    else:
        if token.poll == poll:
            selected_choice.votes += 1
            token.delete()
            selected_choice.save()
            return HttpResponseRedirect(reverse('vote:success', args=(poll_identifier,)))
        else:
            return handle_vote_error(poll, request, "invalid token.", token_string)


def success(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    return render(request, 'vote/success.html', {'poll': poll})


def manage(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    error_message = None
    if request.method == 'POST':
        token = request.POST['token']
        if poll.creator_token == token:
            poll.is_active = False
            poll.save()
            return HttpResponseRedirect(reverse('vote:result', args=(poll_identifier,)))
        error_message = 'Wrong management token'
    context = {
        'poll': poll,
        'error_message': error_message,
    }
    return render(request, 'vote/manage.html', context)


def results(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    amount_redeemed_tokens, amount_remaining_tokens, amount_tokens_total = poll.get_amount_used_unused()
    if poll.is_active:
        return HttpResponseRedirect(reverse('vote:poll', args=(poll_identifier,)))
    return render(request, 'vote/results.html', {
      'poll': poll,
      'amount_redeemed_tokens': amount_redeemed_tokens,
      'amount_remaining_tokens': amount_remaining_tokens,
      'amount_tokens_total': amount_tokens_total,
    })
