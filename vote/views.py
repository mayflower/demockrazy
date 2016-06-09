from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from .models import Poll, Choice, Token


def poll(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    return render(request, 'vote/poll.html', {'poll': poll})


def index(request):
    return render(request, 'vote/index.html')


def create(request):
    p_title = request.POST['title']
    p_description = request.POST['description']
    poll = Poll(title=p_title, question_text=p_description)
    poll.save()
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
    return render(request, 'vote/results.html', {'poll': poll})
