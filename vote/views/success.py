from django.shortcuts import get_object_or_404, render

from vote.models import Poll


def success(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier=poll_identifier)
    return render(request, 'vote/success.html', {'poll': poll})

