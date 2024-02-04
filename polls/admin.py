from django.contrib import admin

from polls.models import Poll, Question, Choice, Answer


class PollAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


admin.site.register(Poll, PollAdmin)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'type')
    list_filter = ('type',)
    search_fields = ('question_text',)


admin.site.register(Question, QuestionAdmin)


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', )
    list_filter = ('choice_text', )
    search_fields = ('choice_text',)


admin.site.register(Choice, ChoiceAdmin)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'choice', 'poll')
    list_filter = ('poll', 'question', 'user')
    search_fields = ('user__username', 'question__question_text')


admin.site.register(Answer, AnswerAdmin)
