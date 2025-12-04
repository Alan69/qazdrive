from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # Teachers
    path('teachers/', views.teachers_list, name='teachers'),
    path('teachers/add/', views.teacher_add, name='teacher_add'),
    path('teachers/<int:teacher_id>/edit/', views.teacher_edit, name='teacher_edit'),
    
    # Driving Instructors
    path('drivers/', views.drivers_list, name='drivers'),
    path('drivers/add/', views.driver_add, name='driver_add'),
    path('drivers/<int:driver_id>/edit/', views.driver_edit, name='driver_edit'),
    
    # Production Masters
    path('masters/', views.masters_list, name='masters'),
    path('masters/add/', views.master_add, name='master_add'),
    path('masters/<int:master_id>/edit/', views.master_edit, name='master_edit'),
    
    # Employees/Workers
    path('workers/', views.workers_list, name='workers'),
    path('workers/add/', views.worker_add, name='worker_add'),
    path('workers/<int:worker_id>/edit/', views.worker_edit, name='worker_edit'),
]

