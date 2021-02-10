from rest_framework import serializers
from .models import MeetingRoom, Reservation, Invitation
from django.db.models import Q


class MeetingRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingRoom
        fields = "__all__"


class InvitationSerializer(serializers.ModelSerializer):
    reservation = serializers.CharField(read_only=True)

    class Meta:
        model = Invitation
        fields = ["invitee", "status", "reservation"]


class ReservationSerializer(serializers.ModelSerializer):
    guests = InvitationSerializer(many=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "title",
            "from_date",
            "to_date",
            "room",
            "creator",
            "guests",
        ]

    def create(self, validated_data):
        invitations = validated_data.pop("guests")
        reservation = Reservation.objects.create(**validated_data)
        for invitation in invitations:
            Invitation.objects.create(reservation=reservation, **invitation)
        return reservation

    def validate(self, data):
        """
        Check if the room is empty at the given time
        """
        room = data["room"]
        start_time = data["from_date"]
        end_time = data["to_date"]
        self.validate_times(start_time, end_time)
        same_time_same_room = Reservation.objects.filter(room=room).filter(
            Q(from_date=start_time, to_date=end_time)
            | Q(from_date__lte=start_time, to_date__gt=start_time)
            | Q(from_date__lt=end_time, to_date__gte=end_time)
        )
        if same_time_same_room.exists():
            raise serializers.ValidationError(
                "There is an overlap with another reservation"
            )
        return data

    def validate_times(self, start, end):
        if start >= end:
            raise serializers.ValidationError(
                "Start time must be set earlier than end time"
            )
