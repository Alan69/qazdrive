from django.urls import  path
from .views import load_task

urlpatterns = [
    path('load_task/<int:id_task>/<str:lang>/', load_task, name = "load_task"),
]