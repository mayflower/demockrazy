from django.db import models
from django.utils.timezone import now

import uuid

class Poll(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    publication_date = models.DateTimeField('date published', default=now)
    active = models.BooleanField(default=True)

    amount_tokens = models.IntegerField()

    def __str__(self):
        return self.title

class Question(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def vote(self, answer):
        raise NotImplemented("Vote function must be implemented in question sub-type")

class SingleChoiceQuestion(Question):
    def vote(self, answer):
        try:
            choice = SingleChoiceChoice.objects.get(id=answer['choiceId'])
        except SingleChoiceChoice.DoesNotExist:
            raise Exception('not a valid choice for this question')

        if choice.question == self:
            choice.increment()

class Choice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

class SingleChoiceChoice(Choice):
    question = models.ForeignKey(SingleChoiceQuestion, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    count = models.IntegerField(default = 0)

    def __str__(self):
        return self.text

    def increment(self):
        self.count += 1
        self.save()


class Token(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
