from django.db import models
from django.utils.translation import gettext as _
from django.conf import settings


class MeetingRoom(models.Model):
    title = models.CharField(max_length=200)


class Reservation(models.Model):
    title = models.CharField(max_length=200)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    room = models.ForeignKey(
        MeetingRoom,
        related_name="reservations",
        on_delete=models.CASCADE,
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="meetings_created",
        on_delete=models.CASCADE,
    )
    attendee = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Invitation", related_name="meetings"
    )

    def __str__(self):
        return f"{self.title} from {self.from_date} to {self.to_date}"


class Invitation(models.Model):
    ATTENDING = "attending"
    NOT_ATTENDING = "not attending"
    MAYBE = "maybe"
    STATUS = (
        (ATTENDING, _("The guest will attend the meeting")),
        (NOT_ATTENDING, _("The guest will not attend the meeting")),
        (MAYBE, _("The guest hasn't decided yet")),
    )
    status = models.PositiveSmallIntegerField(choices=STATUS, default=3)
    reservation = models.ForeignKey(
        Reservation, related_name="guests", on_delete=models.CASCADE
    )
    invitee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="invitations",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.invitee} - {self.status}"
