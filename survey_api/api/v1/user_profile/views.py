from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.user_profile.models import Profile
from apps.user_profile.permissions import IsProfileOwner
from apps.user_profile.serializers import ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsProfileOwner()]
        else:
            return [AllowAny()]
