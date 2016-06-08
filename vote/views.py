from django.http import HttpResponse
from django.shortcuts import render
from .models import Poll


def index(request):
    return render(request, 'vote/index.html')

def list(request):
    polls = Poll.objects.order_by('-pub_date')
    context = {
        'polls': polls
    }
    return render(request, 'vote/list.html', context)
