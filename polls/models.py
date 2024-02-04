from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone

from users.models import User


class Question(models.Model):
    class QuestionType(models.TextChoices):
        TYPE1 = 'type1', 'Type 1'
        TYPE2 = 'type2', 'Type 2'

    question_text = models.TextField(unique=True)
    type = models.CharField(max_length=200, choices=QuestionType.choices)


class Choice(models.Model):
    class ChoiceText(models.TextChoices):
        YES = 'yes', 'yes'
        NO = 'no', 'no'
        NOT_SURE = 'not_sure', 'not sure'

    choice_text = models.CharField(max_length=200, choices=ChoiceText.choices)


class Poll(models.Model):
    name = models.TextField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    questions = models.ManyToManyField(Question, related_name='polls')

    def get_absolute_url(self):
        return reverse_lazy('poll', args=[self.pk])

    def get_stats_url(self):
        return reverse_lazy('stats', args=[self.pk])


class Answer(models.Model):
    choice = models.ForeignKey(Choice, on_delete=models.PROTECT, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name='question_answers')
    poll = models.ForeignKey(Poll, on_delete=models.PROTECT, related_name='poll_answers')
