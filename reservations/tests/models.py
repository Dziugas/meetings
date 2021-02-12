from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import datetime
from reservations.models import MeetingRoom, Reservation, Invitation


User = get_user_model()


class TestModels(TestCase):
    def test_reservation_str(self):
        room = MeetingRoom.objects.create(title="Engineer Room")
        employee = User.objects.create(username="jim", password="123456789")
        reservation = Reservation.objects.create(
            title="Agile meeting",
            from_date=datetime(2021, 2, 28, 13, 00, 00),
            to_date=datetime(2021, 2, 28, 14, 00, 00),
            room=room,
            creator=employee,
        )
        self.assertEqual(
            str(reservation),
            "Agile meeting from 2021-02-28 13:00:00 to 2021-02-28 14:00:00",
        )

    def test_invitation_str(self):
        room = MeetingRoom.objects.create(title="Engineer Room")
        employee = User.objects.create(username="jim", password="123456789")
        reservation = Reservation.objects.create(
            title="Agile meeting",
            from_date=datetime(2021, 2, 28, 13, 00, 00),
            to_date=datetime(2021, 2, 28, 14, 00, 00),
            room=room,
            creator=employee,
        )
        invitation = Invitation.objects.create(
            reservation=reservation, invitee=employee
        )
        self.assertEqual(str(invitation), "jim - maybe")
