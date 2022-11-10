from django.db import models

# Create your models here.
class Question(models.Model):
    # id_question = models.IntegerField(primary_key=True)
    id_task = models.IntegerField(null=True, blank=True)
    theme_number = models.IntegerField(null=True, blank=True)
    partition_number = models.IntegerField(null=True, blank=True)
    subpartition_number = models.IntegerField(null=True, blank=True)
    order_num_question = models.IntegerField(null=True, blank=True)
    url_image = models.CharField(max_length=255, null=True, blank=True, default="None")
    question = models.CharField(max_length=255, null=True, default="None")

    def __str__(self):
        return self.question

class Answer(models.Model):
    # id_answer = models.IntegerField(primary_key=True)
    id_question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order_num_answer = models.IntegerField(null=True, blank=True)
    correctly = models.CharField(max_length=255, null=True, blank=True)
    answer = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.answer