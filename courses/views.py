from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Course, Video, UserVideoProgress

# Import custom chunked upload views and models
from chunked_upload_override.views import ChunkedUploadView, ChunkedUploadCompleteView
from chunked_upload.models import ChunkedUpload
from chunked_upload_override.constants import http_status
import os
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

# Chunked upload views
class VideoChunkedUploadView(ChunkedUploadView):
    model = ChunkedUpload
    field_name = 'file'

    def check_permissions(self, request):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            raise ChunkedUploadView.PermissionDenied

class VideoChunkedUploadCompleteView(ChunkedUploadCompleteView):
    model = ChunkedUpload
    
    def check_permissions(self, request):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            raise ChunkedUploadView.PermissionDenied

    def on_completion(self, uploaded_file, request):
        # Get the uploaded file
        course_id = request.POST.get('course_id')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        language = request.POST.get('language')
        order = request.POST.get('order', 1)
        
        # Verify the course exists
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Course not found'}, status=400)
        
        # Get the file extension
        _, ext = os.path.splitext(uploaded_file.name)
        
        # Create a unique filename
        filename = f'course_videos/{course_id}_{language}_{title}_{uploaded_file.id}{ext}'
        
        # Create a new Video object
        video = Video.objects.create(
            course=course,
            title=title,
            description=description,
            language=language,
            order=int(order),
            video_file=filename
        )
        
        # Move the file to the permanent location
        destination_path = os.path.join('media', filename)
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        with open(destination_path, 'wb') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        return {'video_id': video.id}

    def get_response_data(self, chunked_upload, request):
        try:
            response = self.on_completion(chunked_upload.file, request)
            return response
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

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
