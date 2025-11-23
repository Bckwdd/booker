from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from events.models import Booking, Event

User = get_user_model()


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class EventSerializer(serializers.ModelSerializer):
    seats_taken = serializers.ReadOnlyField()
    owner = OwnerSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ("id", "title", "description", "datetime", "max_seats", "seats_taken", "owner")

    def validate_datetime(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Event cannot be in the past.")
        return value


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ("id", "event", "seats_booked")

    def validate(self, data):
        event = data.get("event")
        seats_requested = data.get("seats_booked")

        seats_available = event.max_seats - event.seats_taken
        if seats_requested > seats_available:
            raise serializers.ValidationError("Not enough seats available.")
        return data


class BookingListSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ("id", "event", "seats_booked", "created_at")
