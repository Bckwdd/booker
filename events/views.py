from django.db import IntegrityError, transaction
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from events.models import Booking, Event
from events.serializers import BookingListSerializer, BookingSerializer, EventSerializer


@extend_schema(tags=["Events"])
class EventViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = EventSerializer

    def get_queryset(self):
        return (
            Event.objects.all()
            .select_related("owner")
            .annotate(calculated_seats_taken=Coalesce(Sum("bookings__seats_booked"), Value(0)))
            .order_by("id")
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(
        request=inline_serializer(
            name="BookingRequest",
            fields={"seats_booked": serializers.IntegerField(default=1, min_value=1)},
        ),
        responses={
            201: BookingListSerializer,
            400: {"description": "Error: Not enough seats or duplicate booking."},
            404: {"description": "Event not found."},
        },
    )
    @action(detail=True, methods=["post"])
    def book(self, request, pk=None):
        with transaction.atomic():
            try:
                event = Event.objects.select_for_update().get(pk=pk)
            except Event.DoesNotExist:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

            input_serializer = BookingSerializer(
                data={"event": event.id, "seats_booked": request.data.get("seats_booked", 1)}
            )

            if input_serializer.is_valid():
                try:
                    booking_instance = input_serializer.save(user=request.user)
                    output_serializer = BookingListSerializer(booking_instance)
                    return Response(output_serializer.data, status=status.HTTP_201_CREATED)
                except IntegrityError:
                    return Response(
                        {"error": "You have already booked this event."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["My"])
class MyViewSet(viewsets.ViewSet):
    @extend_schema(responses=EventSerializer(many=True))
    @action(detail=False, methods=["get"], url_path="events")
    def events(self, request):
        events = (
            Event.objects.filter(owner=request.user)
            .select_related("owner")
            .annotate(calculated_seats_taken=Coalesce(Sum("bookings__seats_booked"), Value(0)))
        )
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    @extend_schema(responses=BookingListSerializer(many=True))
    @action(detail=False, methods=["get"], url_path="bookings")
    def bookings(self, request):
        bookings = Booking.objects.filter(user=request.user).select_related("event", "event__owner")
        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data)
