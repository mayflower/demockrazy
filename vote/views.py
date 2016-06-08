from django.http import HttpResponse
from django.template import loader

from .models import Poll

def poll(request, poll_identifier):
    poll = Poll.objects.get(identifier = poll_identifier)
    template = loader.get_template('vote/poll.html')
    context = {
        'poll': poll,
    }
    return HttpResponse(template.render(context, request))