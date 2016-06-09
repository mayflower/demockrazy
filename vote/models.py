from django.db import models
from django.utils.timezone import now

import random
import string



def rand_string(length):
    return ''.join(random.SystemRandom().choice(
        string.ascii_letters + string.digits
    ) for _ in range(length))


def mk_admin_token():
    return rand_string(256)


def mk_identifier():
    id = rand_string(64)
    if not Poll.objects.filter(identifier=id).exists():
        return id
    else:
        return mk_identifier()


def mk_token():
    tok = rand_string(128)
    if not Token.objects.filter(token_string=tok).exists():
        return tok
    else:
        return mk_token()


class Poll(models.Model):
    title = models.CharField(max_length=200)
    question_text = models.TextField()
    pub_date = models.DateTimeField('date published', default=now, blank=True)
    creator_token = models.CharField(max_length=512, default=mk_admin_token)
    identifier = models.CharField(max_length=64, default=mk_identifier)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.TextField()
    votes = models.IntegerField(default=0)

    def __str__(self):
        return "%s - %s" % (self.poll, self.choice_text )


class Token(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    token_string = models.CharField(max_length=128)

    def __str__(self):
        return "%s Token" % self.poll
