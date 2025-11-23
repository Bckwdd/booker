from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from users.views import UserRegistrationAV

urlpatterns = [
    path("register/", UserRegistrationAV.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
]
