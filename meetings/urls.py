from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from accounts.urls import router as accounts_router
from reservations.urls import router as reservations_router

router = routers.DefaultRouter()
router.registry.extend(accounts_router.registry)
router.registry.extend(reservations_router.registry)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
