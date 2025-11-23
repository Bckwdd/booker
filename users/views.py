from rest_framework import generics, permissions

from users.serializers import UserRegistrationSerializer


class UserRegistrationAV(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
