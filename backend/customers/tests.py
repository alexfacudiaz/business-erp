from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Customer


# Create your tests here.
User = get_user_model()


class CustomerAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email='usuario@test.com',
            password='password123',
            first_name='Juan',
            last_name='Pérez',
        )  # type: ignore

        self.group = Group.objects.create(name='USUARIO')
        self.user.groups.add(self.group)

        permissions = Permission.objects.filter(
            content_type__app_label='customers',
            content_type__model='customer',
            codename__in=[
                'activate_customer',
                'add_customer',
                'change_customer',
                'deactivate_customer',
                'view_customer',
            ],
        )

        self.group.permissions.set(permissions)

        self.customer = Customer.objects.create(
            customer_type=Customer.CustomerType.PERSON,
            tax_id='20123456789',
            first_name='Pedro',
            last_name='Gómez',
            email='pedro@test.com',
        )

        self.url = '/api/customers/'

    def authenticate(self):
        self.client.force_authenticate(user=self.user) # type: ignore

    def test_authenticated_user_can_list_customers(self):
        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data['results']), # type: ignore
            1,
        )

    def test_unauthenticated_user_cannot_access_customers(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_create_person_customer(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                'customer_type': 'PERSON',
                'tax_id': '20987654321',
                'first_name': 'Ana',
                'last_name': 'López',
                'email': 'ana@test.com',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Customer.objects.filter(
                tax_id='20987654321',
            ).exists()
        )

    def test_user_can_create_company_customer(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                'customer_type': 'COMPANY',
                'tax_id': '30765432109',
                'business_name': 'Empresa Test S.A.',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Customer.objects.filter(
                tax_id='30765432109',
            ).exists()
        )

    def test_user_cannot_create_invalid_person(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                'customer_type': 'PERSON',
                'first_name': 'Ana',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_cannot_create_invalid_company(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                'customer_type': 'COMPANY',
                'first_name': 'Ana',
                'last_name': 'López',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_can_update_customer(self):
        self.authenticate()

        response = self.client.patch(
            f'{self.url}{self.customer.pk}/',
            {
                'email': 'nuevo@test.com',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.customer.refresh_from_db()

        self.assertEqual(
            self.customer.email,
            'nuevo@test.com',
        )

    def test_user_can_deactivate_customer(self):
        self.authenticate()

        response = self.client.post(
            f'{self.url}{self.customer.pk}/deactivate/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.customer.refresh_from_db()

        self.assertFalse(
            self.customer.is_active,
        )

    def test_user_can_activate_customer(self):
        self.customer.is_active = False
        self.customer.save()

        self.authenticate()

        response = self.client.post(
            f'{self.url}{self.customer.pk}/activate/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.customer.refresh_from_db()

        self.assertTrue(
            self.customer.is_active,
        )

    def test_can_filter_customers_by_type(self):
        Customer.objects.create(
            customer_type=Customer.CustomerType.COMPANY,
            tax_id='30777777777',
            business_name='Otra Empresa S.A.',
        )

        self.authenticate()

        response = self.client.get(
            self.url,
            {'customer_type': 'COMPANY'},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data['results']), # type: ignore
            1,
        )

        self.assertEqual(
            response.data['results'][0]['customer_type'], # type: ignore
            'COMPANY',
        )

    def test_can_search_customers(self):
        self.authenticate()

        response = self.client.get(
            self.url,
            {'search': 'Pedro'},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data['results']), # type: ignore
            1,
        )

        self.assertEqual(
            response.data['results'][0]['first_name'], # type: ignore
            'Pedro',
        )

    def test_can_order_customers(self):
        Customer.objects.create(
            customer_type=Customer.CustomerType.PERSON,
            tax_id='20999999999',
            first_name='Ana',
            last_name='Gómez',
        )

        self.authenticate()

        response = self.client.get(
            self.url,
            {'ordering': 'first_name'},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['results'][0]['first_name'], # type: ignore
            'Ana',
        )

    def test_cannot_create_customer_with_duplicate_tax_id(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                'customer_type': 'PERSON',
                'tax_id': self.customer.tax_id,
                'first_name': 'Ana',
                'last_name': 'López',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_cannot_deactivate_already_inactive_customer(self):
        self.customer.is_active = False
        self.customer.save()

        self.authenticate()

        response = self.client.post(
            f'{self.url}{self.customer.pk}/deactivate/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_cannot_activate_already_active_customer(self):
        self.authenticate()

        response = self.client.post(
            f'{self.url}{self.customer.pk}/activate/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_cannot_delete_customer(self):
        self.authenticate()

        response = self.client.delete(
            f'{self.url}{self.customer.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.customer.refresh_from_db()

        self.assertTrue(
            self.customer.is_active,
        )

        self.assertTrue(
            Customer.objects.filter(
                pk=self.customer.pk,
            ).exists()
        )

    def test_user_with_delete_permission_can_delete_customer(self):
        delete_permission = Permission.objects.get(
            content_type__app_label='customers',
            content_type__model='customer',
            codename='delete_customer',
        )

        self.group.permissions.add(delete_permission)

        self.authenticate()

        response = self.client.delete(
            f'{self.url}{self.customer.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Customer.objects.filter(
                pk=self.customer.pk,
            ).exists()
        )