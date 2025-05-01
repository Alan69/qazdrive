from django.db import models
from userconf.models import User
import uuid
import os

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

class Video(models.Model):
    LANGUAGE_CHOICES = [
        ('russian', 'Russian'),
        ('kazakh', 'Kazakh'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_file = models.FileField(upload_to='course_videos/')
    thumbnail = models.ImageField(upload_to='video_thumbnails/', null=True, blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    order = models.IntegerField(help_text='Order of video in the course')
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_language_display()})"
    
    class Meta:
        verbose_name = 'Видео'
        verbose_name_plural = 'Видео'
        ordering = ['order']

class UserVideoProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_progress')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='user_progress')
    last_position = models.PositiveIntegerField(default=0, help_text='Last position in seconds')
    is_completed = models.BooleanField(default=False)
    watched_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'video']
        verbose_name = 'Прогресс просмотра'
        verbose_name_plural = 'Прогресс просмотров'
    
    def __str__(self):
        return f"{self.user.first_name} - {self.video.title} - {'Completed' if self.is_completed else 'In progress'}"
