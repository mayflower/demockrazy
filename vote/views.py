from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from .models import Poll, Choice, Token


def poll(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    return render(request, 'vote/poll.html', {'poll': poll})


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
        for choice in choices:
            choice_obj  = Choice(poll = poll, choice_text = choice)
            choice_obj.save()
    p_title = request.POST['title']
    p_description = request.POST['description']
    creator_mail  = request.POST['creator_mail']
    voter_mails = request.POST['voter_mails']
    choices = request.POST['choices']
    voter_mails = parse_mails(voter_mails)
    choices = parse_choices(choices)
    poll = Poll(title=p_title, question_text=p_description)
    poll.save()
    create_choice_objects(choices, poll)
    return render(request, 'vote/create.html')


def vote(request, poll_identifier):
    def handle_vote_error(poll, request, message):
        return render(request, 'vote/poll.html', {
            'poll': poll,
            'error_message': message,
        })

    poll = get_object_or_404(Poll, identifier=poll_identifier)
    if not poll.is_active:
        return HttpResponseRedirect(reverse('vote:result', args=(poll_identifier,)))
    try:
        token = Token.objects.get(token_string=request.POST['token'])
        selected_choice = poll.choice_set.get(pk=request.POST['choice'])
    except KeyError:
        return handle_vote_error(poll, request, "Please fill out all fields.")
    except Choice.DoesNotExist:
        return handle_vote_error(poll, request, "You didn't select a choice.")
    except Token.DoesNotExist:
        return handle_vote_error(poll, request, "invalid token.")
    else:
        if token.poll == poll:
            selected_choice.votes += 1
            token.delete()
            selected_choice.save()
            return HttpResponseRedirect(reverse('vote:success', args=(poll_identifier,)))
        else:
            return handle_vote_error(poll, request, "invalid token.")


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
    if poll.is_active:
      return HttpResponseRedirect(reverse('vote:vote', args=(poll_identifier,)))
    return render(request, 'vote/results.html', {'poll': poll})
