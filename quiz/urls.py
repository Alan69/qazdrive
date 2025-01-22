from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.category, name='categories'),
    path('<int:category_id>/', views.quiz, name='quiz'),
]
