from django.urls import  path
from .views import *

urlpatterns = [
    path('post_order/<str:product>/<int:sum>', post_order, name ="post_order"),
    path('check_order/', check_order, name="check_order"),
]