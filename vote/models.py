from django.db import models
from django.utils.timezone import now



class Poll(models.Model):
    title = models.CharField(max_length=200)
    question_text = models.TextField()
    pub_date = models.DateTimeField('date published', default=now, blank=True)
    creator_token = models.CharField(max_length=512)
    is_active = models.BooleanField(default=True)
    identifier = models.CharField(max_length=64)

    def __str__(self):
        return self.title

class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.TextField()
    votes = models.IntegerField(default=0)


class Token(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    token_string = models.CharField(max_length=128)
