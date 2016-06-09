from django.db import models
from django.utils.timezone import now
from django.db.models.signals import pre_save

import random
import string


class Poll(models.Model):
    title = models.CharField(max_length=200)
    question_text = models.TextField()
    pub_date = models.DateTimeField('date published', default=now, blank=True)
    creator_token = models.CharField(max_length=512)
    identifier = models.CharField(max_length=64, default="")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


def initialize_randoms(sender, instance, *args, **kwargs):
    instance.creator_token = instance.creator_token or rand_string(128)
    instance.identifier = instance.identifier or get_identifier()


def rand_string(length):
    return ''.join(random.SystemRandom().choice(
        string.ascii_letters + string.digits
    ) for _ in range(length))


def get_identifier():
    id = rand_string(64)
    if not Poll.objects.filter(identifier=id).exists():
        return id
    else:
        return get_identifier()


pre_save.connect(initialize_randoms, Poll)

class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.TextField()
    votes = models.IntegerField(default=0)


class Token(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    token_string = models.CharField(max_length=128)
