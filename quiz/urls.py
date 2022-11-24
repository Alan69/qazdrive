from django.urls import  path
from .views import category, quiz

urlpatterns = [
    path('', category, name='category'),
    path('<id>/', quiz, name='quiz'),
]