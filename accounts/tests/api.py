from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, force_authenticate
from rest_framework import status


User = get_user_model()


class UserTests(APITestCase):
    def test_anonymous_cannot_see_users(self):
        users_url = reverse("users-list")
        response = self.client.get(users_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_users_can_see_users(self):
        user = User.objects.create_user(username="jim", password="123456")
        users_url = reverse("users-list")
        self.client.force_authenticate(user=user)
        response = self.client.get(users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["username"], "jim")
