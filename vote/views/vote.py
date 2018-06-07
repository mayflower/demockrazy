from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from vote.models import Poll, Choice, Token

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
