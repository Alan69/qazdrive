from django.contrib import admin
from .models import Course, Video, UserVideoProgress

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    search_fields = ['title', 'description']
    inlines = [VideoInline]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'language', 'order', 'created_at']
    list_filter = ['course', 'language']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['course', 'order']

@admin.register(UserVideoProgress)
class UserVideoProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'last_position', 'is_completed', 'watched_at']
    list_filter = ['is_completed', 'watched_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__phone_number', 'video__title']
    readonly_fields = ['watched_at']
