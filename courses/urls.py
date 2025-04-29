from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
    path('video/<int:video_id>/progress/', views.update_video_progress, name='update_progress'),
    
    # Chunked upload URLs
    path('upload/', views.upload_video_form, name='upload_video_form'),
    path('upload/course/<int:course_id>/', views.upload_video_form, name='upload_video_form_course'),
    path('api/upload/chunked/', views.VideoChunkedUploadView.as_view(), name='api_chunked_upload'),
    path('api/upload/chunked/complete/', views.VideoChunkedUploadCompleteView.as_view(), name='api_chunked_upload_complete'),
] 