from django.urls import include, path
from rest_framework import routers

from api.v1.user_profile.views import ProfileViewSet

router = routers.DefaultRouter()
router.register(r"profiles", ProfileViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
