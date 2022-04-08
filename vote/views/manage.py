
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from vote.models import Poll


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
    amount_redeemed_tokens, amount_remaining_tokens, amount_tokens_total = poll.get_amount_used_unused()
    context = {
        'poll': poll,
        'amount_redeemed_tokens': amount_redeemed_tokens,
        'amount_remaining_tokens': amount_remaining_tokens,
        'amount_tokens_total': amount_tokens_total,
        'error_message': error_message,
    }
    return render(request, 'vote/manage.html', context)
