from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.db.models import F
from django.shortcuts import render, get_object_or_404

from .models import POLL_TYPES, Poll, Choice, Token, PersistentValidationToken


def send_mail_or_print(args, print_only=not settings.VOTE_SEND_MAILS):
    if print_only:
        print(*args)
    else:
        send_mail(*args, fail_silently=False)

def poll(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    token = request.GET.get('token', "Please enter your voting token")
    amount_redeemed_tokens, amount_remaining_tokens, amount_tokens_total = poll.get_amount_used_unused()
    if poll.is_active:
        return render(request, 'vote/poll.html',
                      {'poll': poll, 'token': token, "amount_redeemed_tokens": amount_redeemed_tokens,
                       "amount_remaining_tokens": amount_remaining_tokens, "amount_tokens_total": amount_tokens_total,
                       "validation_token": poll.get_validation_token()})
    else:
        return HttpResponseRedirect(reverse('vote:result', args=(poll_identifier,)))

def index(request):
    validation_token_string = request.GET.get('validation_token', None)
    context = {}
    if validation_token_string:
        validation_token=PersistentValidationToken.objects.get(token_string=validation_token_string)
        if validation_token.is_validated:
            context['validation_token'] = validation_token
    return render(request, 'vote/index.html', context)

def validation_request(request):
    message = None
    if request.method == 'POST':
        creator_mail = request.POST['creator_mail']
        validation_token = PersistentValidationToken(creator_mail=creator_mail)
        validation_token.save()
        validation_url = settings.VOTE_BASE_URL + reverse('vote:validate')
        args = ('demockrazy: Confirm your Mail',
                settings.VOTE_VALIDATION_TEXT % {
                    'validation_url_with_token': "%s?validation_token=%s" % ( validation_url, validation_token.token_string )
                },
                settings.VOTE_MAIL_FROM,
                [creator_mail],
                )
        send_mail_or_print(args)
        message = "Please check your mail"
    return render(request, 'vote/validation_request.html', { "message": message })

def process_validation_request(request):
    def handle_validation_error(request, message):
        return render(request, 'vote/validation.html', {
            'message': message,
        })
    validation_token_string = request.GET.get('validation_token', "")
    if validation_token_string:
        try:
            validation_token  = PersistentValidationToken.objects.get(token_string=validation_token_string)
        except PersistentValidationToken.DoesNotExist:
            return handle_validation_error(request, "Invalid token.")
        validation_token.is_validated = True
        validation_token.save()
        return HttpResponseRedirect(reverse('vote:index') + "?validation_token=%s" % validation_token_string)
    return HttpResponseRedirect(reverse('vote:validation_request'))
        
def manage(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    error_message = None
    if not poll.is_active:
        return HttpResponseRedirect(reverse('vote:result', args=(poll_identifier,)))
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

    def send_creator_mail(poll, creator_mail, creator_token, print_only=False):
        manage_url = settings.VOTE_BASE_URL + reverse('vote:manage', args=(poll.identifier,))
        args = ('demockrazy: You created a new poll',
                "Hi, you just created a new poll that is manageable at %(manage_url)s\nYour admin token is: %(creator_token)s\nThank you for flying with LuftHansa" % {
                    "manage_url": manage_url, "creator_token": creator_token},
                settings.VOTE_MAIL_FROM,
                [creator_mail],
                )
        send_mail_or_print(args, print_only)

    def send_mails_with_tokens(poll, voter_mails, tokens, print_only=False):
        token_strings = [token.token_string for token in tokens]
        for voter_mail in voter_mails:
            poll_url_with_token = settings.VOTE_BASE_URL + reverse('vote:poll', args=(
            poll.identifier,)) + '?token=' + token_strings.pop()
            args = (settings.VOTE_MAIL_SUBJECT,
                    settings.VOTE_MAIL_TEXT % {"poll_url_with_token": poll_url_with_token,
                                               "vote_base_url": settings.VOTE_BASE_URL},
                    settings.VOTE_MAIL_FROM,
                    [voter_mail],
                    )
            send_mail_or_print(args, print_only)

    p_title = request.POST['title']
    p_type = request.POST['type']
    if p_type not in POLL_TYPES:
        raise Exception('Invalid poll type')
    p_description = request.POST['description']
    creator_mail = request.POST['creator_mail']
    voter_mails = request.POST['voter_mails']
    choices = request.POST['choices']
    validation_token = None
    if 'validation_token' in request.POST:
        validation_token_string = request.POST['validation_token']
        validation_token = PersistentValidationToken.objects.get(token_string=validation_token_string)
        if validation_token.creator_mail != creator_mail:
            raise ValidationError("Creator mail does not match validated mail")
        if validation_token.is_validated != True:
            raise ValidatoinError("Validation token not valid")
    voter_mails = parse_mails(voter_mails)
    choices = parse_choices(choices)
    poll = Poll(title=p_title, type=p_type, num_tokens=len(voter_mails), question_text=p_description)
    poll.save()
    if validation_token:
        validation_token.poll = poll
        validation_token.save()
    choice_objects = create_choice_objects(choices, poll)
    tokens = create_token_objects(poll, len(voter_mails))
    send_creator_mail(poll, creator_mail, poll.creator_token, not settings.VOTE_SEND_MAILS)
    send_mails_with_tokens(poll, voter_mails, tokens, not settings.VOTE_SEND_MAILS)
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

    def close_poll_if_all_tokens_redeemed(poll):
        amount_redeemed_tokens, amount_remaining_tokens, amount_redeemed_tokens = poll.get_amount_used_unused()
        if amount_remaining_tokens == 0:
            poll.is_active = False
            poll.save()

    poll = get_object_or_404(Poll, identifier=poll_identifier)
    if not poll.is_active:
        return HttpResponseRedirect(reverse('vote:result', args=(poll_identifier,)))
    try:
        with transaction.atomic():
            token_string = request.POST['token']
            token = Token.objects.get(token_string=request.POST['token'])
            if token.poll == poll:
                if poll.type == 'multiple_choice':
                    for choice in Choice.objects.filter(poll=poll):
                        if request.POST['choice%i' % choice.id] == 'yes':
                            choice.votes = F('votes') + 1
                            choice.save()
                else:
                    selected_choice = poll.choice_set.get(pk=request.POST['choice'])
                    selected_choice.votes = F('votes') + 1
                    selected_choice.save()
                token.delete()
                close_poll_if_all_tokens_redeemed(poll)
                return HttpResponseRedirect(reverse('vote:success', args=(poll_identifier,)))
            else:
                return handle_vote_error(poll, request, "invalid token.", token_string)

    except KeyError:
        return handle_vote_error(poll, request, "Please fill out all fields.", token_string)
    except Choice.DoesNotExist:
        return handle_vote_error(poll, request, "You didn't select a choice.", token_string)
    except Token.DoesNotExist:
        return handle_vote_error(poll, request, "invalid token.", token_string)


def success(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    return render(request, 'vote/success.html', {'poll': poll})


def manage(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    error_message = None
    if not poll.is_active:
        return HttpResponseRedirect(reverse('vote:result', args=(poll_identifier,)))
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
