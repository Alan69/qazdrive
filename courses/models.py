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

class ChunkedVideoUpload(models.Model):
    """Model for tracking chunked uploads of large video files"""
    STATUS_UPLOADING = 1
    STATUS_COMPLETED = 2
    STATUS_FAILED = 3
    
    STATUS_CHOICES = [
        (STATUS_UPLOADING, 'Uploading'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]
    
    upload_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    file = models.FileField(upload_to='uploads/chunked/', max_length=255)
    filename = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chunked_uploads')
    offset = models.BigIntegerField(default=0)
    file_size = models.BigIntegerField(default=0)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_UPLOADING)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=10, choices=Video.LANGUAGE_CHOICES, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    order = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = 'Chunked Video Upload'
        verbose_name_plural = 'Chunked Video Uploads'
    
    def __str__(self):
        return f"{self.filename} - {self.get_status_display()} ({self.offset} bytes)"
    
    def append_chunk(self, chunk):
        """Append a chunk to the file"""
        self.file.open(mode='ab')  # append binary mode
        for content in chunk.chunks():
            self.file.write(content)
        self.offset += chunk.size
        self.file.close()
        self.save()
        return self
    
    def get_target_path(self):
        """Get the final path for the completed video"""
        _, ext = os.path.splitext(self.filename)
        return f'course_videos/{self.course.id}_{self.language}_{self.pk}{ext}'
