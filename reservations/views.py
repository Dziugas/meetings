from rest_framework import viewsets
from .models import MeetingRoom, Reservation, Invitation
from .serializers import (
    MeetingRoomSerializer,
    ReservationSerializer,
    InvitationSerializer,
)


class ReservationViewset(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer


class InvitationViewset(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer


class MeetingRoomViewset(viewsets.ModelViewSet):
    queryset = MeetingRoom.objects.all()
    serializer_class = MeetingRoomSerializer
