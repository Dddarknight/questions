from collections import defaultdict

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.db.models import Q, Count, Case, When, IntegerField, Prefetch
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView

from polls.models import Poll, Answer, Question, Choice


class PollsView(LoginRequiredMixin, ListView):
    template_name = 'polls/polls.html'
    model = Poll


class PollView(LoginRequiredMixin, TemplateView):
    template_name = 'polls/poll.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poll_id = kwargs['pk']
        poll = Poll.objects.prefetch_related(
            Prefetch('questions', queryset=Question.objects.exclude(
                type__in=self.get_questions_types_to_exclude()))
        ).get(id=poll_id)
        context['poll'] = poll
        choices = Choice.objects.all()
        context['choices'] = choices
        return context

    def get_questions_types_to_exclude(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            question_types_agg = (
                Answer.objects
                .filter(user=user)
                .values('question__type')
                .annotate(
                    no_answers=Count(Case(When(choice__choice_text='no', then=1),
                                          output_field=IntegerField())),
                    not_no_answers=Count(Case(When(~Q(choice__choice_text='no'), then=1),
                                              output_field=IntegerField()))
                )
            )
            return [
                item['question__type'] for item in question_types_agg if
                item['not_no_answers'] == 0 and item['no_answers'] > 0
            ]
        return None


@login_required
def submit_answers(request):
    if request.method == 'POST':
        user = request.user
        poll_id = request.POST.get('poll_id')

        for key, value in request.POST.items():
            if not key.isnumeric(): continue
            question_id, choice_id = int(key), int(value)
            question = Question.objects.get(id=question_id)
            choice = Choice.objects.get(id=choice_id)
            poll = Poll.objects.get(id=poll_id)

            Answer.objects.update_or_create(
                user=user,
                question=question,
                poll=poll,
                choice=choice,
            )

        return redirect(reverse_lazy('polls'))
    else:
        return HttpResponse("Invalid request", status=400)


@method_decorator(staff_member_required, name='dispatch')
class StatsMenu(ListView):
    template_name = 'polls/stats_menu.html'
    model = Poll


@method_decorator(staff_member_required, name='dispatch')
class StatsView(TemplateView):
    template_name = 'polls/stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poll_id = kwargs['pk']
        all_poll_users = self.get_all_poll_users(poll_id)
        context['all_poll_users'] = all_poll_users
        context['questions'] = self.get_questions_stats(poll_id, all_poll_users)
        return context

    @staticmethod
    def get_all_poll_users(poll_id):
        all_poll_users_sql = f"""
            SELECT count(distinct a.user_id) FROM polls_answer a 
            WHERE a.poll_id = {poll_id}
        """
        with connection.cursor() as cursor:
            cursor.execute(all_poll_users_sql)
            all_poll_users_data = cursor.fetchone()
            return all_poll_users_data[0] if all_poll_users_data else 0

    @staticmethod
    def get_questions_stats(poll_id, users):
        users_per_question_sql = f"""
            WITH users_count_per_question as (
                SELECT 
                    count(distinct a.user_id) as users_count,
                    CAST(COUNT(DISTINCT a.user_id) AS REAL) / {users} * 100 as users_part,
                    q.id as question_id,
                    a.poll_id as poll_id
                FROM polls_answer a 
                JOIN polls_question q on q.id = a.question_id
                WHERE a.poll_id = {poll_id}
                GROUP BY q.id
            )
            SELECT 
                DENSE_RANK () OVER (PARTITION BY uq.poll_id ORDER BY uq.users_count desc) AS "question_row",
                uq.users_count as users_count,
                uq.users_part as users_part,
                q.id,
                q.question_text
            FROM users_count_per_question uq
            JOIN polls_question q on q.id = uq.question_id
            WHERE uq.poll_id = {poll_id};
        """
        users_per_question_and_choice_sql = f"""
            WITH users_count_per_question as (
                SELECT 
                    count(distinct a.user_id) as users_count,
                    q.id as question_id,
                    a.poll_id as poll_id
                FROM polls_answer a 
                JOIN polls_question q on q.id = a.question_id
                WHERE a.poll_id = {poll_id}
                GROUP BY q.id
            ),
            users_count_per_question_and_choice as (
                SELECT 
                    count(distinct a.user_id) as users_count,
                    CAST(COUNT(DISTINCT a.user_id) AS REAL) / uq.users_count * 100 as users_part,
                    q.id as question_id,
                    c.id as choice_id,
                    a.poll_id as poll_id
                FROM polls_answer a 
                JOIN polls_question q on q.id = a.question_id
                JOIN polls_choice c on c.id = a.choice_id
                JOIN users_count_per_question uq on uq.question_id = q.id
                WHERE a.poll_id = {poll_id}
                GROUP BY q.id, c.id
            )
            SELECT 
                DENSE_RANK () OVER (PARTITION BY uqc.question_id ORDER BY uqc.users_count desc) AS "question_choice_row",
                uqc.users_count as users_count,
                uqc.users_part as users_part,
                q.id,
                q.question_text,
                c.choice_text
            FROM users_count_per_question_and_choice uqc
            JOIN polls_question q on q.id = uqc.question_id
            JOIN polls_choice c on c.id = uqc.choice_id
            WHERE uqc.poll_id = {poll_id};
        """

        with connection.cursor() as cursor:
            cursor.execute(users_per_question_sql)
            users_per_question_data = cursor.fetchall()
            cursor.execute(users_per_question_and_choice_sql)
            users_per_question_and_choice_data = cursor.fetchall()

        users_per_question_and_choice_dict = defaultdict(list)
        for entry in users_per_question_and_choice_data:
            users_per_question_and_choice_dict[entry[3]].append(
                {
                    'row_number': entry[0],
                    'users_count': entry[1],
                    'users_part': entry[2],
                    'choice': entry[5],
                }
            )

        return [
            {
                'question_id': entry[3],
                'question_text': entry[4],
                'row_number': entry[0],
                'users_count': entry[1],
                'users_part': entry[2],
                'choices_stats': users_per_question_and_choice_dict[entry[3]]
            }
            for entry in users_per_question_data
        ]
