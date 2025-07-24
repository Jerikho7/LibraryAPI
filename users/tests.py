from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User


class UserTests(APITestCase):
    def setUp(self):
        self.password = "TestPass123"
        self.user = User.objects.create_user(email="user@example.com", password=self.password)
        self.client.force_authenticate(user=self.user)

    def test_register_user(self):
        url = reverse("users:register")
        data = {"email": "newuser@example.com", "password": "NewPass123", "password2": "NewPass123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_login_user(self):
        url = reverse("users:login")
        self.client.logout()
        data = {"email": self.user.email, "password": self.password}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_view_profile(self):
        url = reverse("users:user-profile-detail", kwargs={"pk": self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_update_profile(self):
        url = reverse("users:user-profile-detail", kwargs={"pk": self.user.pk})
        data = {"first_name": "Иван"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Иван")

    def test_change_password(self):
        url = reverse("users:change-password")
        data = {"old_password": self.password, "new_password": "NewPass123"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass123"))

    def test_deactivate_own_profile(self):
        url = reverse("users:user-profile-me")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_create_disallowed_in_viewset(self):
        url = reverse("users:user-profile-list")  # ← это ок
        data = {"email": "test@invalid.com", "password": "test123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 405)
