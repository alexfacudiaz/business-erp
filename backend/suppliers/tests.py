from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Supplier


# Create your tests here.
User = get_user_model()


class SupplierAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email='usuario@test.com',
            password='password123',
            first_name='Juan',
            last_name='Pérez',
        )  # type: ignore

        self.group = Group.objects.create(
            name='USUARIO',
        )

        self.user.groups.add(
            self.group,
        )

        permissions = Permission.objects.filter(
            content_type__app_label='suppliers',
            content_type__model='supplier',
            codename__in=[
                'add_supplier',
                'change_supplier',
                'view_supplier',
                'activate_supplier',
                'deactivate_supplier',
            ],
        )

        self.group.permissions.set(
            permissions,
        )

        self.supplier = Supplier.objects.create(
            supplier_type=Supplier.SupplierType.PERSON,
            tax_id='20123456789',
            first_name='Pedro',
            last_name='Gómez',
            email='pedro@test.com',
        )

        self.url = '/api/suppliers/'

    def authenticate(self):
        self.client.force_authenticate( # type: ignore
            user=self.user,
        )

    def test_authenticated_user_can_list_suppliers(self):
        self.authenticate()

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data['results']),  # type: ignore
            1,
        )

    def test_unauthenticated_user_cannot_access_suppliers(self):
        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_retrieve_supplier(self):
        self.authenticate()

        response = self.client.get(
            f'{self.url}{self.supplier.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['id'],  # type: ignore
            self.supplier.pk,
        )

        self.assertEqual(
            response.data['tax_id'],  # type: ignore
            self.supplier.tax_id,
        )

    def test_unauthenticated_user_cannot_retrieve_supplier(self):
        response = self.client.get(
            f'{self.url}{self.supplier.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_create_person_supplier(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                'supplier_type': 'PERSON',
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
            Supplier.objects.filter(
                tax_id='20987654321',
            ).exists()
        )

    def test_user_can_create_company_supplier(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                'supplier_type': 'COMPANY',
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
            Supplier.objects.filter(
                tax_id='30765432109',
            ).exists()
        )

    def test_user_cannot_create_invalid_person_supplier(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                'supplier_type': 'PERSON',
                'first_name': 'Ana',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_cannot_create_invalid_company_supplier(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                'supplier_type': 'COMPANY',
                'first_name': 'Ana',
                'last_name': 'López',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_can_update_supplier(self):
        self.authenticate()

        response = self.client.patch(
            f'{self.url}{self.supplier.pk}/',
            {
                'email': 'nuevo@test.com',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.supplier.refresh_from_db()

        self.assertEqual(
            self.supplier.email,
            'nuevo@test.com',
        )

    def test_cannot_create_supplier_with_duplicate_tax_id(self):
        self.authenticate()

        response = self.client.post(
            self.url,
            {
                'supplier_type': 'PERSON',
                'tax_id': self.supplier.tax_id,
                'first_name': 'Ana',
                'last_name': 'López',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_can_deactivate_supplier(self):
        self.authenticate()

        response = self.client.post(
            f'{self.url}{self.supplier.pk}/deactivate/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.supplier.refresh_from_db()

        self.assertFalse(
            self.supplier.is_active,
        )

    def test_user_can_activate_supplier(self):
        self.supplier.is_active = False
        self.supplier.save()

        self.authenticate()

        response = self.client.post(
            f'{self.url}{self.supplier.pk}/activate/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.supplier.refresh_from_db()

        self.assertTrue(
            self.supplier.is_active,
        )

    def test_cannot_deactivate_already_inactive_supplier(self):
        self.supplier.is_active = False
        self.supplier.save()

        self.authenticate()

        response = self.client.post(
            f'{self.url}{self.supplier.pk}/deactivate/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_cannot_activate_already_active_supplier(self):
        self.authenticate()

        response = self.client.post(
            f'{self.url}{self.supplier.pk}/activate/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_cannot_delete_supplier(self):
        self.authenticate()

        response = self.client.delete(
            f'{self.url}{self.supplier.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.supplier.refresh_from_db()

        self.assertTrue(
            self.supplier.is_active,
        )

        self.assertTrue(
            Supplier.objects.filter(
                pk=self.supplier.pk,
            ).exists()
        )

    def test_unauthenticated_user_cannot_deactivate_supplier(self):
        response = self.client.post(
            f'{self.url}{self.supplier.pk}/deactivate/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_can_filter_suppliers_by_type(self):
        Supplier.objects.create(
            supplier_type=Supplier.SupplierType.COMPANY,
            tax_id='30777777777',
            business_name='Otra Empresa S.A.',
        )

        self.authenticate()

        response = self.client.get(
            self.url,
            {'supplier_type': 'COMPANY'},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data['results']),  # type: ignore
            1,
        )

        self.assertEqual(
            response.data['results'][0]['supplier_type'],  # type: ignore
            'COMPANY',
        )

    def test_can_search_suppliers(self):
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
            len(response.data['results']),  # type: ignore
            1,
        )

        self.assertEqual(
            response.data['results'][0]['first_name'],  # type: ignore
            'Pedro',
        )

    def test_can_order_suppliers(self):
        Supplier.objects.create(
            supplier_type=Supplier.SupplierType.PERSON,
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
            response.data['results'][0]['first_name'],  # type: ignore
            'Ana',
        )