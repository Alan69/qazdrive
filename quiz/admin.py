from django.contrib import admin
from .models import Question, Category, Result
# Register your models here.
from import_export.admin import ImportExportModelAdmin
from import_export import fields, resources, widgets


class QuestionResource(resources.ModelResource):

    category = fields.Field(
        attribute="id",
        column_name="id",
        widget=widgets.ForeignKeyWidget(Category),
    )
    
    class Meta:
        model = Question

class QuestionAdmin(ImportExportModelAdmin):
    resource_classes = [QuestionResource]
    # search_fields = ('id', 'question')
    # list_display = ('id', 'question')


# class AnswerResource(resources.ModelResource):

#     question = fields.Field(
#         attribute="question_id",
#         column_name="question_id",
#         widget=widgets.ForeignKeyWidget(Question),
#     )

#     class Meta:
#         model = Answer

# class AnswerAdmin(ImportExportModelAdmin):
#     resource_classes = [AnswerResource]

admin.site.register(Question, QuestionAdmin)
# admin.site.register(Answer, AnswerAdmin)
admin.site.register(Category)
admin.site.register(Result)

