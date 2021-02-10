from django.db.models.query_utils import Q
from rest_framework import viewsets
from .models import MeetingRoom, Reservation, Invitation
from .serializers import (
    MeetingRoomSerializer,
    ReservationSerializer,
    InvitationSerializer,
)


class ReservationViewset(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer

    def get_queryset(self):
        """
        Shows only reservations related to the provided user by the
        provided user_id query parameter in the URL
        """
        queryset = Reservation.objects.all()
        user_id = self.request.query_params.get("user_id", None)
        if user_id is not None:
            queryset = queryset.filter(
                Q(creator__id=user_id) | Q(attendees__id=user_id)
            )
        return queryset


class InvitationViewset(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer


class MeetingRoomViewset(viewsets.ModelViewSet):
    queryset = MeetingRoom.objects.all()
    serializer_class = MeetingRoomSerializer
