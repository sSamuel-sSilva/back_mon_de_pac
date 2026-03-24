from django.test import TestCase
from importlib import import_module, reload

# Create your tests here.
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.test import APITestCase

from users.models import Address, Patient
from users.permissions import CustomPermission
from users.serializers import (
    CompanionReadSerializer,
    CompanionWriteSerializer,
    CustomUserWriteSerializer,
)
from users.services import PatientCreateService, PatientUpdateService
from users.views import CompanionViewSet, PatientViewSet

User = get_user_model()


class UsersUrlsTests(SimpleTestCase):
    def test_users_urls_module_loads(self):
        module = import_module("users.urls")
        reload(module)
        self.assertTrue(hasattr(module, "urlpatterns"))


class CustomUserWriteSerializerTests(TestCase):
    def test_serializer_hashes_password_on_create(self):
        serializer = CustomUserWriteSerializer(
            data={
                "username": "admin-user",
                "password": "SenhaSegura123",
                "cpf": "12345678901",
                "type": User.UserType.ADMIN,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertNotEqual(user.password, "SenhaSegura123")
        self.assertTrue(user.check_password("SenhaSegura123"))


class PatientViewSetPermissionTests(SimpleTestCase):
    def test_create_uses_allow_any(self):
        view = PatientViewSet()
        view.action = "create"

        permissions = view.get_permissions()

        self.assertEqual([type(permission) for permission in permissions], [AllowAny])

    def test_list_uses_is_authenticated(self):
        view = PatientViewSet()
        view.action = "list"

        permissions = view.get_permissions()

        self.assertEqual([type(permission) for permission in permissions], [IsAuthenticated])

    def test_update_uses_custom_permission(self):
        view = PatientViewSet()
        view.action = "update"

        permissions = view.get_permissions()

        self.assertEqual([type(permission) for permission in permissions], [CustomPermission])


class CompanionViewSetSerializerTests(SimpleTestCase):
    def test_list_uses_read_serializer(self):
        view = CompanionViewSet()
        view.action = "list"

        serializer_class = view.get_serializer_class()

        self.assertIs(serializer_class, CompanionReadSerializer)

    def test_create_uses_write_serializer(self):
        view = CompanionViewSet()
        view.action = "create"

        serializer_class = view.get_serializer_class()

        self.assertIs(serializer_class, CompanionWriteSerializer)


class PatientServicesTests(TestCase):
    def test_patient_create_service_creates_related_records(self):
        patient = PatientCreateService.create(
            user_data={
                "username": "paciente-1",
                "password": "SenhaSegura123",
                "cpf": "11122233344",
                "type": User.UserType.ADMIN,
            },
            address_data={
                "cep": "50000-000",
                "street": "Rua A",
                "number": "10",
                "city": "Recife",
                "state": "PE",
                "complement": "",
                "neighborhood": "Centro",
            },
            patient_data={
                "name": "Paciente Teste",
                "telephone": "81999999999",
            },
        )

        user = patient.user
        self.assertEqual(user.type, User.UserType.PACIENTE)
        self.assertTrue(user.check_password("SenhaSegura123"))
        self.assertTrue(Address.objects.filter(user=user).exists())
        self.assertTrue(Patient.objects.filter(user=user).exists())

    def test_patient_update_service_rejects_duplicate_username(self):
        other_user = User.objects.create_user(
            username="ja-existe",
            password="SenhaSegura123",
            cpf="99988877766",
            type=User.UserType.PACIENTE,
        )
        patient_user = User.objects.create_user(
            username="paciente-2",
            password="SenhaSegura123",
            cpf="12312312312",
            type=User.UserType.PACIENTE,
        )
        address = Address.objects.create(
            user=patient_user,
            cep="50000-000",
            street="Rua B",
            number="20",
            city="Recife",
            state="PE",
            complement="",
            neighborhood="Boa Vista",
        )
        patient = Patient.objects.create(
            user=patient_user,
            address=address,
            name="Paciente 2",
            telephone="81888888888",
        )

        with self.assertRaisesMessage(Exception, "Username já cadastrado por outro usuário"):
            PatientUpdateService.update(
                patient,
                user_data={"username": other_user.username},
                address_data={},
                patient_data={},
            )


class PatientViewSetApiTests(APITestCase):
    def _patient_payload(self, username="paciente-api", cpf="32165498700"):
        return {
            "user": {
                "username": username,
                "password": "SenhaSegura123",
                "cpf": cpf,
                "type": User.UserType.ADMIN,
            },
            "address": {
                "cep": "50000-000",
                "street": "Rua API",
                "number": "200",
                "city": "Recife",
                "state": "PE",
                "complement": "",
                "neighborhood": "Boa Vista",
            },
            "patient": {
                "name": "Paciente API",
                "telephone": "81977777777",
            },
        }

    def test_create_returns_patient_query_detail_shape(self):
        response = self.client.post(reverse("patient-list"), self._patient_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), {"id", "name", "telephone", "user", "address"})
        self.assertEqual(response.data["user"]["username"], "paciente-api")
        self.assertIn("cpf", response.data["user"])
        self.assertEqual(
            set(response.data["address"].keys()),
            {"id", "cep", "street", "number", "city", "state", "complement", "neighborhood"},
        )
        self.assertEqual(response.data["address"]["street"], "Rua API")

    def test_list_non_staff_only_sees_own_patient(self):
        user_a = User.objects.create_user(
            username="user-a",
            password="SenhaSegura123",
            cpf="12345123451",
            type=User.UserType.PACIENTE,
        )
        user_b = User.objects.create_user(
            username="user-b",
            password="SenhaSegura123",
            cpf="12345123452",
            type=User.UserType.PACIENTE,
        )

        address_a = Address.objects.create(
            user=user_a,
            cep="50000-000",
            street="Rua A",
            number="1",
            city="Recife",
            state="PE",
            complement="",
            neighborhood="Centro",
        )
        address_b = Address.objects.create(
            user=user_b,
            cep="50000-001",
            street="Rua B",
            number="2",
            city="Recife",
            state="PE",
            complement="",
            neighborhood="Boa Vista",
        )

        patient_a = Patient.objects.create(user=user_a, address=address_a, name="Paciente A", telephone="81900000001")
        Patient.objects.create(user=user_b, address=address_b, name="Paciente B", telephone="81900000002")

        self.client.force_authenticate(user=user_a)
        response = self.client.get(reverse("patient-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], patient_a.id)
        self.assertEqual(set(response.data[0]["address"].keys()), {"id", "city", "state"})

    def test_retrieve_non_staff_cannot_access_other_patient(self):
        owner = User.objects.create_user(
            username="owner",
            password="SenhaSegura123",
            cpf="77766655544",
            type=User.UserType.PACIENTE,
        )
        outsider = User.objects.create_user(
            username="outsider",
            password="SenhaSegura123",
            cpf="11122233300",
            type=User.UserType.PACIENTE,
        )

        address_owner = Address.objects.create(
            user=owner,
            cep="50000-010",
            street="Rua Owner",
            number="10",
            city="Recife",
            state="PE",
            complement="",
            neighborhood="Centro",
        )
        patient_owner = Patient.objects.create(
            user=owner,
            address=address_owner,
            name="Paciente Owner",
            telephone="81912345678",
        )

        self.client.force_authenticate(user=outsider)
        response = self.client.get(reverse("patient-detail", args=[patient_owner.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_returns_full_address_fields(self):
        owner = User.objects.create_user(
            username="owner-detail",
            password="SenhaSegura123",
            cpf="55544433322",
            type=User.UserType.PACIENTE,
        )
        address = Address.objects.create(
            user=owner,
            cep="50000-010",
            street="Rua Completa",
            number="10",
            city="Recife",
            state="PE",
            complement="Casa",
            neighborhood="Centro",
        )
        patient = Patient.objects.create(
            user=owner,
            address=address,
            name="Paciente Owner",
            telephone="81912345678",
        )

        self.client.force_authenticate(user=owner)
        response = self.client.get(reverse("patient-detail", args=[patient.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["address"]["street"], "Rua Completa")
        self.assertIn("neighborhood", response.data["address"])