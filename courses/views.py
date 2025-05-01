from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.views import View
from django.core.files.base import ContentFile
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import Course, Video, UserVideoProgress
import os
import json
import shutil
from datetime import timedelta

@login_required
def course_list(request):
    """View to list all available courses"""
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    """View to show details of a specific course and its videos based on language"""
    course = get_object_or_404(Course, id=course_id)
    
    # Get the selected language or default to Russian
    language = request.GET.get('language', 'russian')
    
    # Get all videos for this course in the selected language
    videos = Video.objects.filter(course=course, language=language).order_by('order')
    
    # Get user progress for these videos
    if request.user.is_authenticated:
        for video in videos:
            progress, created = UserVideoProgress.objects.get_or_create(
                user=request.user,
                video=video
            )
            video.progress = progress
    
    # Count videos in each language
    russian_count = Video.objects.filter(course=course, language='russian').count()
    kazakh_count = Video.objects.filter(course=course, language='kazakh').count()
    
    context = {
        'course': course,
        'videos': videos,
        'selected_language': language,
        'russian_count': russian_count,
        'kazakh_count': kazakh_count,
    }
    
    return render(request, 'courses/course_detail.html', context)

@login_required
def video_detail(request, video_id):
    """View to display and play a specific video"""
    video = get_object_or_404(Video, id=video_id)
    course = video.course
    
    # Get user progress for this video
    progress, created = UserVideoProgress.objects.get_or_create(
        user=request.user,
        video=video
    )
    
    # Get next and previous videos in same language and course
    next_video = Video.objects.filter(
        course=course, 
        language=video.language, 
        order__gt=video.order
    ).order_by('order').first()
    
    prev_video = Video.objects.filter(
        course=course, 
        language=video.language, 
        order__lt=video.order
    ).order_by('-order').first()
    
    # Get all videos in the same language for this course for the sidebar
    course_videos = Video.objects.filter(
        course=course,
        language=video.language
    ).order_by('order')
    
    # Get progress for all videos in sidebar
    for v in course_videos:
        v_progress, _ = UserVideoProgress.objects.get_or_create(
            user=request.user,
            video=v
        )
        v.progress = v_progress
    
    context = {
        'video': video,
        'course': course,
        'progress': progress,
        'next_video': next_video,
        'prev_video': prev_video,
        'course_videos': course_videos,
    }
    
    return render(request, 'courses/video_detail.html', context)

@login_required
def update_video_progress(request, video_id):
    """AJAX view to update video progress"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        video = get_object_or_404(Video, id=video_id)
        
        # Get current position from AJAX request
        current_position = int(request.POST.get('current_position', 0))
        is_completed = request.POST.get('is_completed') == 'true'
        
        # Update or create progress record
        progress, created = UserVideoProgress.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={
                'last_position': current_position,
                'is_completed': is_completed
            }
        )
        
        if not created:
            progress.last_position = current_position
            if is_completed:
                progress.is_completed = True
            progress.save()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

# Custom chunked upload views
@login_required
def upload_video_form(request, course_id=None):
    """Form for uploading a new video with chunked upload"""
    
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        courses = [course]
    else:
        courses = Course.objects.all()
        
    context = {
        'courses': courses,
        'selected_course_id': course_id,
    }
    
    return render(request, 'courses/upload_video.html', context)