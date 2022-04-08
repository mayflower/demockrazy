from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from vote.models import Poll


def results(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    amount_redeemed_tokens, amount_remaining_tokens, amount_tokens_total = poll.get_amount_used_unused()
    if poll.is_active:
        return HttpResponseRedirect(reverse('vote:polls:poll', args=(poll_identifier,)))
    return render(request, 'vote/results.html', {
        'poll': poll,
        'amount_redeemed_tokens': amount_redeemed_tokens,
        'amount_remaining_tokens': amount_remaining_tokens,
        'amount_tokens_total': amount_tokens_total,
    })
