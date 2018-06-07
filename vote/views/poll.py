from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from vote.models import Poll, Token


def poll(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    token = request.GET.get('token', '')
    error_message = None
    if token:
        try:
            token_object = Token.objects.get(token_string=token)
        except Token.DoesNotExist:
            error_message = "This token is invalid. Maybe you voted already?"
    amount_redeemed_tokens, amount_remaining_tokens, amount_tokens_total = poll.get_amount_used_unused()
    if poll.is_active:
        return render(request, 'vote/poll.html', {
            'poll': poll,
            'token': token,
            'amount_redeemed_tokens': amount_redeemed_tokens,
            'amount_remaining_tokens': amount_remaining_tokens,
            'amount_tokens_total': amount_tokens_total,
            'error_message': error_message,
        })
    else:
        return HttpResponseRedirect(reverse('vote:result', args=(poll_identifier,)))
