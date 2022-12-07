from .models import User
from rest_framework import viewsets
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions

class UserAPIView(APIView):
    @staticmethod
    def get(request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
