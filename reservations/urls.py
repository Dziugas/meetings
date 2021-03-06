from rest_framework import routers
from .views import MeetingRoomViewset, ReservationViewset

app_name = "reservations"

router = routers.SimpleRouter()
router.register(r"reservations", ReservationViewset, basename="reservations")
router.register(r"rooms", MeetingRoomViewset, basename="rooms")
