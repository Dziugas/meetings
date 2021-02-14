from rest_framework import serializers
from .models import MeetingRoom, Reservation, Invitation
from django.db.models import Q


class InvitationSerializer(serializers.ModelSerializer):
    reservation = serializers.CharField(read_only=True)

    class Meta:
        model = Invitation
        fields = ["invitee", "status", "reservation"]


class ReservationSerializer(serializers.ModelSerializer):
    guests = InvitationSerializer(many=True, required=False)

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
        invitations = validated_data.get("guests", None)
        if invitations:
            invitations = validated_data.pop("guests")
            reservation = Reservation.objects.create(**validated_data)
            for invitation in invitations:
                Invitation.objects.create(
                    reservation=reservation, **invitation
                )
        else:
            reservation = Reservation.objects.create(**validated_data)
        return reservation

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.from_date = validated_data.get(
            "from_date", instance.from_date
        )
        instance.to_date = validated_data.get("to_date", instance.to_date)
        instance.room = validated_data.get("room", instance.room)
        instance.creator = validated_data.get("creator", instance.creator)
        instance.save()

        new_invitation_data = validated_data.get("guests", [])
        self.update_invitation_data(new_invitation_data)

        return instance

    def update_invitation_data(self, new_invitation_data):
        old_invitation_data = self.instance.guests.all()
        if old_invitation_data:

            if len(new_invitation_data) == len(old_invitation_data):
                for number, old_invitation in enumerate(old_invitation_data):
                    old_invitation.invitee = new_invitation_data[number].get(
                        "invitee", old_invitation.invitee
                    )
                    old_invitation.save()

            elif len(new_invitation_data) > len(old_invitation_data):
                for number, new_invitation in enumerate(new_invitation_data):
                    if number < len(old_invitation_data):
                        old_invitation_data[
                            number
                        ].invitee = new_invitation.get(
                            "invitee", old_invitation_data[number].invitee
                        )
                        old_invitation_data[number].save()
                    else:
                        Invitation.objects.create(
                            reservation=self.instance, **new_invitation
                        )

            elif len(new_invitation_data) < len(old_invitation_data):
                for number, old_invitation in enumerate(old_invitation_data):
                    if number < len(new_invitation_data):
                        old_invitation.invitee = new_invitation_data[
                            number
                        ].get("invitee", old_invitation.invitee)
                        old_invitation.save()
                    else:
                        old_invitation.delete()
        else:
            for new_invitation in new_invitation_data:
                Invitation.objects.create(
                    reservation=self.instance, **new_invitation
                )

    def validate(self, data):
        """
        Check that the room is empty at the required time, that the meeting
        starts before it ends, and that the creator does not invite himself
        """
        (
            room,
            start_time,
            end_time,
        ) = self.get_data_from_request_data_or_from_instance(data)

        self.validate_times(start_time, end_time)
        self.validate_if_there_are_no_other_meetings_at_the_same_time(
            room, start_time, end_time
        )
        return data

    def get_data_from_request_data_or_from_instance(self, data):
        if "room" in data:
            room = data["room"]
        else:
            room = self.instance.room

        if "from_date" in data:
            start_time = data["from_date"]
        else:
            start_time = self.instance.from_date

        if "to_date" in data:
            end_time = data["to_date"]
        else:
            end_time = self.instance.to_date

        return room, start_time, end_time

    def validate_if_there_are_no_other_meetings_at_the_same_time(
        self, room, start_time, end_time
    ):
        if self.instance:
            reservation_id = self.instance.id
            same_time_same_room = (
                Reservation.objects.exclude(id=reservation_id)
                .filter(room=room)
                .filter(
                    Q(from_date=start_time, to_date=end_time)
                    | Q(from_date__lte=start_time, to_date__gt=start_time)
                    | Q(from_date__lt=end_time, to_date__gte=end_time)
                )
            )
        else:
            same_time_same_room = Reservation.objects.filter(room=room).filter(
                Q(from_date=start_time, to_date=end_time)
                | Q(from_date__lte=start_time, to_date__gt=start_time)
                | Q(from_date__lt=end_time, to_date__gte=end_time)
            )
        if same_time_same_room.exists():
            raise serializers.ValidationError(
                "There is an overlap with another reservation"
            )

    def validate_times(self, start, end):
        if start >= end:
            raise serializers.ValidationError(
                "Start time must be set earlier than end time"
            )


class MeetingRoomSerializer(serializers.ModelSerializer):
    reservations = ReservationSerializer(many=True, required=False)

    class Meta:
        model = MeetingRoom
        fields = "__all__"
