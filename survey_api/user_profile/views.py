from rest_framework import viewsets
from users.models import User
from users.serializers import UserSerializer
from .serializers import ProfileSerializer
from .models import Profile


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer