import threading

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Booking, Event

User = get_user_model()


class RaceConditionTest(TransactionTestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", email="u1@test.com", password="123")
        self.user2 = User.objects.create_user(username="user2", email="u2@test.com", password="123")

        self.event = Event.objects.create(
            owner=self.user1, title="Hot Event", datetime="2025-12-12T12:00:00Z", max_seats=1
        )
        self.url = reverse("event-book", args=[self.event.id])

    def tearDown(self):
        connections.close_all()

    def book_seat(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        try:
            client.post(self.url, {"seats_booked": 1})
        finally:
            connections.close_all()

    def test_race_condition(self):
        t1 = threading.Thread(target=self.book_seat, args=(self.user1,))
        t2 = threading.Thread(target=self.book_seat, args=(self.user2,))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        bookings_count = Booking.objects.filter(event=self.event).count()
        print(f"\nBooked: {bookings_count} of {self.event.max_seats}")

        self.assertEqual(bookings_count, 1, "Race Condition!")


class EventFunctionalTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email="user1@test.com", username="u1", password="123")
        self.user2 = User.objects.create_user(email="user2@test.com", username="u2", password="123")

        self.event1 = Event.objects.create(
            owner=self.user1,
            title="Python Meetup",
            description="Intro to Django",
            datetime="2030-01-01T10:00:00Z",
            max_seats=10,
        )

        self.list_url = reverse("event-list")
        self.book_url = reverse("event-book", args=[self.event1.id])
        self.my_events_url = reverse("my-events")
        self.my_bookings_url = reverse("my-bookings")

    def test_list_events(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        if "seats_taken" in response.data[0]:
            self.assertEqual(response.data[0]["seats_taken"], 0)

    def test_create_event(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "title": "New Party",
            "description": "Party time",
            "datetime": "2030-12-31T23:00:00Z",
            "max_seats": 50,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Event.objects.last().owner, self.user1)

    def test_book_event_logic(self):
        self.client.force_authenticate(user=self.user2)

        res = self.client.post(self.book_url, {"seats_booked": 3})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertIn("event", res.data)

        self.assertEqual(res.data["event"]["id"], self.event1.id)
        self.assertEqual(res.data["seats_booked"], 3)

        self.event1.refresh_from_db()
        self.assertEqual(self.event1.seats_taken, 3)

    def test_my_endpoints(self):
        Booking.objects.create(user=self.user2, event=self.event1, seats_booked=2)

        self.client.force_authenticate(user=self.user1)
        res_ev = self.client.get(self.my_events_url)
        res_bk = self.client.get(self.my_bookings_url)

        self.assertEqual(res_ev.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_ev.data), 1)
        self.assertEqual(len(res_bk.data), 0)

        self.client.force_authenticate(user=self.user2)
        res_ev = self.client.get(self.my_events_url)
        res_bk = self.client.get(self.my_bookings_url)

        self.assertEqual(res_ev.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_ev.data), 0)
        self.assertEqual(len(res_bk.data), 1)

        self.assertEqual(res_bk.data[0]["event"]["title"], "Python Meetup")
