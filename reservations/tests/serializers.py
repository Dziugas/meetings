from datetime import datetime
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.exceptions import ValidationError
from reservations.serializers import ReservationSerializer
from reservations.models import MeetingRoom, Reservation, Invitation

User = get_user_model()


class ReservationSerializerTests(APITestCase):
    def setUp(self):
        self.start = datetime(2021, 5, 5, 11, 0, 0)
        self.end = datetime(2021, 5, 5, 10, 0, 0)
        self.serializer = ReservationSerializer()

    def test_serializer_raises_exception_if_start_date_greater_than_the_end_date(
        self,
    ):

        self.assertRaises(
            ValidationError,
            self.serializer.validate_times,
            self.start,
            self.end,
        )

    def test_serializer_raises_exception_if_event_time_clashes_with_another_event(
        self,
    ):
        room = MeetingRoom.objects.create(title="Games room")
        john = User.objects.create(username="john", password="123456")
        Reservation.objects.create(
            title="Foosball break",
            from_date=self.start,
            to_date=self.end,
            room=room,
            creator=john,
        )

        self.assertRaises(
            ValidationError,
            self.serializer.validate_if_there_are_no_other_meetings_at_the_same_time,
            room,
            self.start,
            self.end,
        )

    def test_serializer_updates_if_update_data_has_more_guests(self):
        room = MeetingRoom.objects.create(title="Games room")
        john = User.objects.create(username="john", password="123456")
        peter = User.objects.create(username="peter", password="123456")
        zigmas = User.objects.create(username="zigmas", password="123456")
        reservation = Reservation.objects.create(
            title="Another foosball break",
            from_date=self.start,
            to_date=self.end,
            room=room,
            creator=john,
        )

        new_invitation_data = [{"invitee": zigmas}, {"invitee": peter}]
        serializer = ReservationSerializer(instance=reservation)
        serializer.update_invitation_data(new_invitation_data)

        updated_invitation_data = reservation.guests.all()
        self.assertEqual(len(updated_invitation_data), 2)

    def test_serializer_updates_if_update_data_has_less_guests(self):
        room = MeetingRoom.objects.create(title="Games room")
        john = User.objects.create(username="john", password="123456")
        peter = User.objects.create(username="peter", password="123456")
        zigmas = User.objects.create(username="zigmas", password="123456")
        reservation = Reservation.objects.create(
            title="Another foosball break",
            from_date=self.start,
            to_date=self.end,
            room=room,
            creator=john,
        )
        Invitation.objects.create(
            reservation=reservation, invitee=peter
        )
        Invitation.objects.create(
            reservation=reservation, invitee=zigmas
        )

        new_invitation_data = [{"invitee": zigmas}]

        serializer = ReservationSerializer(instance=reservation)
        serializer.update_invitation_data(new_invitation_data)

        updated_invitation_data = reservation.guests.all()
        self.assertEqual(len(updated_invitation_data), 1)

    def test_serializer_updates_if_update_data_has_the_same_number_of_guests(
        self,
    ):
        room = MeetingRoom.objects.create(title="Games room")
        john = User.objects.create(username="john", password="123456")
        peter = User.objects.create(username="peter", password="123456")
        zigmas = User.objects.create(username="zigmas", password="123456")
        reservation = Reservation.objects.create(
            title="Another foosball break",
            from_date=self.start,
            to_date=self.end,
            room=room,
            creator=john,
        )
        Invitation.objects.create(
            reservation=reservation, invitee=peter
        )
        new_invitation_data = [{"invitee": zigmas}]

        serializer = ReservationSerializer(instance=reservation)
        serializer.update_invitation_data(new_invitation_data)

        updated_invitation_data = reservation.guests.all()
        new_invitees = [
            invitation.invitee for invitation in updated_invitation_data
        ]
        self.assertEqual(len(updated_invitation_data), 1)
        self.assertEqual(new_invitees[0].username, "zigmas")
