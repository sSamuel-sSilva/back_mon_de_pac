from django.db import transaction
from rest_framework import serializers
from .models import CustomUser, Address, Patient
from .serializers import CustomUserWriteSerializer, AddressWriteSerializer, PatientWriteSerializer


class PatientCreateService:
    @staticmethod
    @transaction.atomic
    def create(user_data, address_data, patient_data):
        if CustomUser.objects.filter(username=user_data["username"]).exists():
            raise serializers.ValidationError({"username": "Username já cadastrado por outro usuário"})

        if CustomUser.objects.filter(cpf=user_data["cpf"]).exists():
            raise serializers.ValidationError({"cpf": "CPF já cadastrado por outro usuário"})

        user = CustomUser.objects.create_user(**user_data, type=CustomUser.UserType.PACIENTE)
        user.set_password(user_data["password"])
        
        address = Address.objects.create(user=user, **address_data)
        patient = Patient.objects.create(user=user, address=address, **patient_data)

        return patient


class PatientUpdateService:
    @staticmethod
    def update(patient, user_data, address_data, patient_data):
        user_instance = patient.user
        address_instance = patient.address

        with transaction.atomic():
            for field, value in user_data.items():
                if field == "password":
                    user_instance.set_password(value)
                else:
                    setattr(user_instance, field, value)
            user_instance.save()

            for field, value in address_data.items():
                setattr(address_instance, field, value)
            address_instance.save()

            for field, value in patient_data.items():
                setattr(patient, field, value)
            patient.save()


        return patient
    
