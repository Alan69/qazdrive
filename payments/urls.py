from django.urls import  path
from .views import *

urlpatterns = [
    path('', get_orders, name = "get_orders"),
    path('post_order/', post_order, name ="post_order"),
]