from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .models import Poll

def poll(request, poll_identifier):
    poll = get_object_or_404(Poll, identifier = poll_identifier)
    return render (request, 'vote/poll.html', {'poll': poll})

def create(request):
    return render (request, 'vote/create.html')
