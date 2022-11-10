from django.contrib import admin
from .models import Question, Answer
# Register your models here.
from import_export.admin import ImportExportModelAdmin
from import_export import fields, resources, widgets


class QuestionResource(resources.ModelResource):

    class Meta:
        model = Question

class QuestionAdmin(ImportExportModelAdmin):
    resource_classes = [QuestionResource]
    search_fields = ('id', 'question')
    list_display = ('id', 'question')


class AnswerResource(resources.ModelResource):

    quiz = fields.Field(
        attribute="id_question",
        column_name="id_question",
        widget=widgets.ForeignKeyWidget(Question),
    )

    class Meta:
        model = Answer

class AnswerAdmin(ImportExportModelAdmin):
    resource_classes = [AnswerResource]

admin.site.register(Question,QuestionAdmin)
admin.site.register(Answer,AnswerAdmin)
