from django.test import TestCase

from .models import *

class PollTest(TestCase):
    def setUp(self):
        p = Poll(title="title", description="description", active=True, amount_tokens=17)
        p.save()
        q = SingleChoiceQuestion(poll=p, title="questiontitle?", description="questiondescription")
        q.save()
        c = SingleChoiceChoice(question=q, text="singlechoicechoicetext!")
        c.save()
        self.choice_id=c.id
        self.question_id=q.id

    def test_single_choice_choice_model(self):
        c=SingleChoiceChoice.objects.get(id=self.choice_id)
        self.assertEqual(c.count, 0)

    def test_single_choice_question_vote_valid(self):
        q = SingleChoiceQuestion.objects.get(id=self.question_id)
        q.vote({
            "choiceId": self.choice_id
        })
        c=SingleChoiceChoice.objects.get(id=self.choice_id)
        self.assertEqual(c.count, 1)

    def test_single_choice_question_vote_invalid(self):
        q = SingleChoiceQuestion.objects.get(id=self.question_id)
        self.assertRaises(Exception, lambda: q.vote({
            "choiceId": "banana"
        }))
        c=SingleChoiceChoice.objects.get(id=self.choice_id)
        self.assertEqual(c.count, 0)

