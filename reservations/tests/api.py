from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, force_authenticate
from rest_framework import status
from datetime import datetime
from reservations.models import MeetingRoom, Reservation, Invitation

User = get_user_model()


class TestRooms(APITestCase):
    def setUp(self):
        self.rooms_url = reverse("rooms-list")
        self.user = User.objects.create(username="jim", password="123456")

    def test_anonymous_cannot_see_rooms(self):
        response = self.client.get(self.rooms_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_user_can_create_room(self):
        self.client.force_authenticate(user=self.user)
        data = {"title": "DevOps Room"}
        response = self.client.post(self.rooms_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "DevOps Room")
        
    def test_room_endpoint_displays_related_reservations(self):
        room = MeetingRoom.objects.create(title="Guest room")
        reservation = Reservation.objects.create(
            title="Guest break",
            from_date="2031-02-27 13:00:00",
            to_date="2031-02-27 15:00:00",
            room=room,
            creator=self.user,
        )
        room_url = f'{self.rooms_url}{room.id}/'
                
        self.client.force_authenticate(user=self.user)
        response = self.client.get(room_url)
        
        self.assertEqual(len(response.data["reservations"]), 1)

class ReservationTests(APITestCase):
    def setUp(self):
        self.reservations_url = reverse("reservations-list")
        self.room = MeetingRoom.objects.create(title="Pythonista room")
        self.user_creator = User.objects.create(
            username="jim", password="123456"
        )
        self.user_invitee = User.objects.create(
            username="tom", password="654321"
        )

    def test_anonymous_cannot_see_reservations(self):
        response = self.client.get(self.reservations_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_user_can_create_reservation(self):
        data = {
            "title": "Python meetup",
            "from_date": "2021-02-27 13:00:00",
            "to_date": "2021-02-27 15:00:00",
            "room": self.room.id,
            "creator": self.user_creator.id,
            "guests": [{"invitee": self.user_invitee.id}],
        }
        self.client.force_authenticate(user=self.user_creator)
        response = self.client.post(
            self.reservations_url, data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_auth_user_can_create_reservation_without_guests(self):
        data = {
            "title": "JS meetup",
            "from_date": "2021-02-26 13:00:00",
            "to_date": "2021-02-26 15:00:00",
            "room": self.room.id,
            "creator": self.user_creator.id,
        }
        self.client.force_authenticate(user=self.user_creator)
        response = self.client.post(
            self.reservations_url, data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_auth_user_cant_create_two_reservations_with_same_time(self):
        data1 = {
            "title": "JS meetup",
            "from_date": "2021-02-26 13:00:00",
            "to_date": "2021-02-26 15:00:00",
            "room": self.room.id,
            "creator": self.user_creator.id,
        }
        data2 = {
            "title": "TS meetup",
            "from_date": "2021-02-26 13:00:00",
            "to_date": "2021-02-26 15:00:00",
            "room": self.room.id,
            "creator": self.user_creator.id,
        }
        self.client.force_authenticate(user=self.user_creator)
        response1 = self.client.post(
            self.reservations_url, data1, format="json"
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        response2 = self.client.post(
            self.reservations_url, data2, format="json"
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response2.data["non_field_errors"][0],
            "There is an overlap with another reservation",
        )

    def test_auth_user_can_filter_reservations_by_user_id(self):
        # create two events
        reservation1 = Reservation.objects.create(
            title="Go meetup 1",
            from_date=datetime(2021, 2, 25, 13, 00, 00),
            to_date=datetime(2021, 2, 25, 14, 00, 00),
            room=self.room,
            creator=self.user_creator,
        )
        Invitation.objects.create(
            reservation=reservation1, invitee=self.user_invitee
        )
        Reservation.objects.create(
            title="Go meetup 2",
            from_date=datetime(2021, 2, 24, 13, 00, 00),
            to_date=datetime(2021, 2, 24, 14, 00, 00),
            room=self.room,
            creator=self.user_creator,
        )

        self.client.force_authenticate(user=self.user_creator)

        # test if creator can see both events after filtering
        filtering_url_user_1 = (
            f"{self.reservations_url}?user_id={self.user_creator.id}"
        )
        response3 = self.client.get(filtering_url_user_1)
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response3.data), 2)
        self.assertEqual(response3.data[0]["title"], "Go meetup 1")
        self.assertEqual(response3.data[1]["title"], "Go meetup 2")

        # test if invitee can see only one event after filtering
        filtering_url_user_2 = (
            f"{self.reservations_url}?user_id={self.user_invitee.id}"
        )
        response4 = self.client.get(filtering_url_user_2)
        self.assertEqual(response4.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response4.data), 1)
        self.assertEqual(response4.data[0]["title"], "Go meetup 1")

    def test_auth_user_can_update_the_reservation(self):
        reservation = Reservation.objects.create(
            title="Agile meeting weekly",
            from_date=datetime(2021, 3, 28, 13, 00, 00),
            to_date=datetime(2021, 3, 28, 14, 00, 00),
            room=self.room,
            creator=self.user_creator,
        )
        Invitation.objects.create(
            reservation=reservation, invitee=self.user_invitee
        )

        data = {
            "title": "Agile meeting monthly",
            "from_date": "2021-03-27 13:00:00",
            "to_date": "2021-03-27 15:00:00",
            "room": self.room.id,
            "creator": self.user_creator.id,
            "guests": [{"invitee": self.user_invitee.id}],
        }

        reservation_url = f"{self.reservations_url}{reservation.id}/"
        self.client.force_authenticate(user=self.user_creator)
        response = self.client.put(reservation_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_user_can_patch_the_reservation(self):
        reservation = Reservation.objects.create(
            title="Agile conference",
            from_date=datetime(2021, 3, 1, 13, 00, 00),
            to_date=datetime(2021, 3, 1, 14, 00, 00),
            room=self.room,
            creator=self.user_creator,
        )
        Invitation.objects.create(
            reservation=reservation, invitee=self.user_invitee
        )

        # lets only change the title and the start date of the event
        data = {
            "title": "Agile super conference",
            "from_date": "2021-03-1 12:00:00",
        }

        reservation_url = f"{self.reservations_url}{reservation.id}/"
        self.client.force_authenticate(user=self.user_creator)
        response = self.client.patch(reservation_url, data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
