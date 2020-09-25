from django.contrib import admin
from .models import *


class QuestionInline(admin.TabularInline):
    model = Question
    ordering = ("order", "type")
    extra = 1

class SurveyAdmin(admin.ModelAdmin):
    list_display = ("name", "status")
    inlines = [QuestionInline]


admin.site.register(Contact)
admin.site.register(Interviewer)
admin.site.register(Client)
admin.site.register(Interviewee)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question)
admin.site.register(Response)
admin.site.register(Answer)
