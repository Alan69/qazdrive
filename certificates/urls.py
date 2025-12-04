from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    # School certificate management
    path('', views.certificates_list, name='list'),
    path('create/', views.certificate_create, name='create'),
    path('create/student/<int:student_id>/', views.certificate_create, name='create_for_student'),
    path('<int:certificate_id>/', views.certificate_detail, name='detail'),
    path('<int:certificate_id>/issue/', views.certificate_issue, name='issue'),
    path('<int:certificate_id>/revoke/', views.certificate_revoke, name='revoke'),
    path('<int:certificate_id>/download/', views.certificate_download, name='download'),
    
    # Public verification
    path('verify/<uuid:uuid>/', views.verify_certificate, name='verify'),
    path('api/verify/<uuid:uuid>/', views.verify_certificate_api, name='verify_api'),
    
    # Student registry verification
    path('verify-student/', views.verify_student, name='verify_student'),
]

