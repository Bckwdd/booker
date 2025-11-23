from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    datetime = models.DateTimeField()
    max_seats = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    @property
    def seats_taken(self):
        if hasattr(self, "calculated_seats_taken"):
            return self.calculated_seats_taken
        return self.bookings.aggregate(total=models.Sum("seats_booked"))["total"] or 0


class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bookings")
    seats_booked = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "event"]

    def __str__(self):
        return f"{self.user.email}: {self.event.title}"
