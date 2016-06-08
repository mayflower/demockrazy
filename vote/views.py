from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from .models import Poll

def poll(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier = poll_identifier)
    return render (request, 'vote/poll.html', {'poll': poll})


def create(request):
    return render (request, 'vote/create.html')


def vote(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    try:
        token = Token.objects.get(token_string=request.POST['token'])
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'vote/poll.html', {
            'poll': poll,
            'error_message': "You didn't select a choice.",
        })
    else:
        if token is not null and token.poll == poll:
            selected_choice.votes += 1
            token.delete()
            selected_choice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(reverse('vote:success', args=(poll_identifier,)))
        else:
            return render(request, 'vote/poll.html', {
                'poll': poll,
                'error_message': "the token does not match the poll.",
            })


def success(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    return render(request, 'vote/success.html', {'poll': poll})


def manage(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier = poll_identifier)
    error_message = None
    if request.method == 'POST':
        token = request.POST['token']
        if poll.creator_token == token:
            poll.is_active = False
            poll.save()
            return HttpResponseRedirect('.')
        error_message = 'Wrong management token'
    context = {
        'poll': poll,
        'error_message': error_message,
    }
    return render(request, 'vote/manage.html', context )
