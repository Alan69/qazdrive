from django.db import models
from userconf.models import User

class Category(models.Model):
    cat_name = models.CharField(max_length=255)

    def __str__(self):
        return self.cat_name

class Question(models.Model):
    question_number = models.IntegerField()
    page = models.IntegerField()
    image_path = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Question {self.question_number}"

class QuestionTranslation(models.Model):
    LANGUAGE_CHOICES = [
        ('russian', 'Russian'),
        ('kazakh', 'Kazakh'),
        ('english', 'English'),
    ]

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    question_text = models.TextField()
    correct_option_index = models.IntegerField()

    class Meta:
        unique_together = ['question', 'language']

    def __str__(self):
        return f"{self.question.question_number} - {self.language}"

class QuestionOption(models.Model):
    translation = models.ForeignKey(QuestionTranslation, on_delete=models.CASCADE, related_name='options')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.translation.question.question_number} - {self.text[:50]}..."

class Result(models.Model):
    created = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    score = models.CharField(max_length=50,verbose_name="Балл")

    def __str__(self):
        return str(self.user.category.cat_name) + "-" + str(self.user) + " " +  str(self.score)
    
    class Meta:
        verbose_name_plural = 'Результаты'