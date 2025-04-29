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

from .models import Course, Video, UserVideoProgress, ChunkedVideoUpload
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

@csrf_exempt
@login_required
@require_POST
def chunked_upload(request):
    """Handle chunked upload requests"""
    # Get upload_id if it exists
    upload_id = request.POST.get('upload_id')
    
    if upload_id:
        # Continue an existing upload
        try:
            chunked_upload = ChunkedVideoUpload.objects.get(
                upload_id=upload_id, 
                user=request.user,
                status=ChunkedVideoUpload.STATUS_UPLOADING
            )
        except ChunkedVideoUpload.DoesNotExist:
            return JsonResponse({
                'error': 'Upload not found or already completed'
            }, status=404)
    else:
        # New upload
        try:
            uploaded_file = request.FILES['file']
            file_size = int(request.POST.get('file_size', 0))
            
            # Create a new chunked upload
            chunked_upload = ChunkedVideoUpload(
                user=request.user,
                filename=uploaded_file.name,
                file_size=file_size
            )
            
            # Initialize the file
            chunked_upload.file.save(uploaded_file.name, ContentFile(''))
            
        except KeyError:
            return JsonResponse({
                'error': 'No file found in request'
            }, status=400)
    
    # Add the chunk to the file
    try:
        chunked_upload.append_chunk(request.FILES['file'])
    except Exception as e:
        chunked_upload.status = ChunkedVideoUpload.STATUS_FAILED
        chunked_upload.save()
        return JsonResponse({
            'error': str(e)
        }, status=500)
    
    # Return response
    return JsonResponse({
        'upload_id': chunked_upload.upload_id,
        'offset': chunked_upload.offset,
        'expires': chunked_upload.created_at + timedelta(days=1)
    })

@csrf_exempt
@login_required
@require_POST
def chunked_upload_complete(request):
    """Complete a chunked upload and create a Video instance"""
    upload_id = request.POST.get('upload_id')
    
    if not upload_id:
        return JsonResponse({
            'error': 'No upload_id provided'
        }, status=400)
    
    try:
        chunked_upload = ChunkedVideoUpload.objects.get(
            upload_id=upload_id, 
            user=request.user, 
            status=ChunkedVideoUpload.STATUS_UPLOADING
        )
    except ChunkedVideoUpload.DoesNotExist:
        return JsonResponse({
            'error': 'Upload not found or already completed'
        }, status=404)
    
    # Get metadata for the video
    try:
        course_id = request.POST.get('course_id')
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        language = request.POST.get('language')
        order = int(request.POST.get('order', 1))
        
        course = Course.objects.get(id=course_id)
        
        # Update chunked upload with metadata
        chunked_upload.course = course
        chunked_upload.title = title
        chunked_upload.description = description
        chunked_upload.language = language
        chunked_upload.order = order
        chunked_upload.status = ChunkedVideoUpload.STATUS_COMPLETED
        chunked_upload.completed_at = timezone.now()
        chunked_upload.save()
        
        # Get the target path for the completed video
        target_path = chunked_upload.get_target_path()
        
        # Create a new Video object
        video = Video(
            course=course,
            title=title,
            description=description,
            language=language,
            order=order,
            video_file=target_path
        )
        
        # Save the video to get its ID
        video.save()
        
        # Move the file to its final destination
        temp_path = os.path.join(settings.MEDIA_ROOT, chunked_upload.file.name)
        final_path = os.path.join(settings.MEDIA_ROOT, target_path)
        
        # Ensure the target directory exists
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        
        # Copy the file to its final destination
        shutil.copy2(temp_path, final_path)
        
        return JsonResponse({
            'status': 'success',
            'video_id': video.id,
            'course_id': course.id
        })
        
    except Course.DoesNotExist:
        return JsonResponse({
            'error': 'Course not found'
        }, status=404)
    except Exception as e:
        # Mark as failed and return error
        chunked_upload.status = ChunkedVideoUpload.STATUS_FAILED
        chunked_upload.save()
        return JsonResponse({
            'error': str(e)
        }, status=500)
