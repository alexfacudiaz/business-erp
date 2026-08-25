from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


User = get_user_model()


class MeViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email='usuario@test.com',
            password='password123',
            first_name='Juan',
            last_name='Pérez',
        ) # type: ignore

        self.url = '/api/users/me/'

    def test_authenticated_user_can_access_me(self):
        self.client.force_authenticate(user=self.user) # type: ignore

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code, # type: ignore
            status.HTTP_200_OK,
        )

    def test_me_returns_authenticated_user_data(self):
        self.client.force_authenticate(user=self.user) # type: ignore

        response = self.client.get(self.url)

        self.assertEqual(
            response.data['id'], # type: ignore
            self.user.pk,
        )
        self.assertEqual(
            response.data['email'], # type: ignore
            self.user.email,
        )
        self.assertEqual(
            response.data['first_name'], # type: ignore
            self.user.first_name,
        )
        self.assertEqual(
            response.data['last_name'], # type: ignore
            self.user.last_name,
        )

    def test_unauthenticated_user_cannot_access_me(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code, # type: ignore
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_me_does_not_expose_password(self):
        self.client.force_authenticate(user=self.user) # type: ignore

        response = self.client.get(self.url)

        self.assertNotIn(
            'password',
            response.data, # type: ignore
        )