import logging
from django.db.models.query_utils import Q
from rest_framework import viewsets
from .models import MeetingRoom, Reservation, Invitation
from .serializers import (
    MeetingRoomSerializer,
    ReservationSerializer,
    InvitationSerializer,
)

logger = logging.getLogger("django")


class ReservationViewset(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer

    def get_queryset(self):
        """
        Shows only reservations related to the provided user, if the
        user_id is provided as a query parameter in the URL
        """
        queryset = Reservation.objects.all()
        user_id = self.request.query_params.get("user_id", None)
        if user_id is not None:
            logger.info(f"Filtering reservations with user_id: {user_id}")
            queryset = queryset.filter(
                Q(creator__id=user_id) | Q(attendees__id=user_id)
            )
        return queryset


class InvitationViewset(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer


class MeetingRoomViewset(viewsets.ModelViewSet):
    serializer_class = MeetingRoomSerializer

    def get_queryset(self):
        """
        Shows only reservations related to the provided user, if the
        user_id is provided as a query parameter in the URL
        """
        queryset = MeetingRoom.objects.all()
        user_id = self.request.query_params.get("user_id", None)
        if user_id is not None:
            logger.info(f"Filtering reservations with user_id: {user_id}")
            queryset = queryset.filter(
                Q(reservations__creator__id=user_id)
                | Q(reservations__attendees__id=user_id),
            ).distinct()
        return queryset
