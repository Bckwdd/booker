from django.contrib import admin

from events.models import Booking, Event

admin.site.register(Event)
admin.site.register(Booking)
