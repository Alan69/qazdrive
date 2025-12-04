from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    # User tickets
    path('', views.user_tickets_list, name='user_tickets'),
    path('create/', views.ticket_create, name='create'),
    path('<int:ticket_id>/', views.ticket_detail, name='detail'),
    
    # School tickets
    path('school/', views.school_tickets_list, name='school_tickets'),
    
    # Admin
    path('admin/', views.admin_tickets_list, name='admin_list'),
    path('admin/<int:ticket_id>/', views.admin_ticket_detail, name='admin_detail'),
]

