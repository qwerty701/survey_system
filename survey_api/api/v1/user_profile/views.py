from rest_framework import viewsets

from apps.user_profile.models import Profile
from apps.user_profile.serializers import ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
