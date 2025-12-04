from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Groups
    path('groups/', views.groups_list, name='groups'),
    path('groups/add/', views.group_add, name='group_add'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    
    # Students
    path('', views.students_list, name='students'),
    path('add/', views.student_add, name='student_add'),
    path('add/group/<int:group_id>/', views.student_add, name='student_add_to_group'),
    path('<int:student_id>/', views.student_detail, name='student_detail'),
    path('<int:student_id>/edit/', views.student_edit, name='student_edit'),
    
    # Documents
    path('<int:student_id>/documents/add/', views.student_document_add, name='document_add'),
    path('<int:student_id>/documents/<int:document_id>/delete/', views.student_document_delete, name='document_delete'),
    
    # Lessons
    path('<int:student_id>/lessons/add/', views.lesson_add, name='lesson_add'),
    
    # API
    path('api/search/', views.student_search_api, name='search_api'),
]

