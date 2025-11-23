from django.urls import include, path
from rest_framework.routers import DefaultRouter

from events.views import EventViewSet, MyViewSet

router = DefaultRouter()

router.register(r"events", EventViewSet, basename="event")
router.register(r"my", MyViewSet, basename="my")

urlpatterns = [path("", include(router.urls))]
