from django.db import models
from userconf.models import User

class Category(models.Model):
    cat_name = models.CharField(max_length=255)

    def __str__(self):
        return self.cat_name

class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    question_text = models.CharField(max_length=255)
    url_image = models.CharField(max_length=255, null=True, blank=True, default="None")

    correctly = models.CharField(max_length=255, null=True, blank=True)
    answer1 = models.CharField(max_length=255, null=True, blank=True)
    answer2 = models.CharField(max_length=255, null=True, blank=True)
    answer3 = models.CharField(max_length=255, null=True, blank=True)
    answer4 = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.question_text

class Result(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    score = models.FloatField(verbose_name="Балл")

    def __str__(self):
        return str(self.category.cat_name) + "-" + self.user.get_full_name() + " " +  str(self.score)
    
    class Meta:
        verbose_name_plural = 'Результаты'