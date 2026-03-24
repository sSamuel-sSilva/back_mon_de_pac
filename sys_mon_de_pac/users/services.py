from django.db import transaction
from rest_framework import serializers
from .models import CustomUser, Address, Patient
from .serializers import CustomUserWriteSerializer, AddressWriteSerializer, PatientWriteSerializer


class PatientCreateService:
    @staticmethod
    @transaction.atomic
    def create(user_data, address_data, patient_data):
        username = user_data["username"]
        cpf = user_data["cpf"]

        if CustomUser.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username já cadastrado por outro usuário"})

        if cpf and CustomUser.objects.filter(cpf=cpf).exists():
            raise serializers.ValidationError({"cpf": "CPF já cadastrado por outro usuário"})

        user = CustomUser.objects.create_user(**user_data, type=CustomUser.UserType.PACIENTE)
        
        address = Address.objects.create(user=user, **address_data)
        patient = Patient.objects.create(user=user, address=address, **patient_data)

        return patient


class PatientUpdateService:
    @staticmethod
    def update(patient, user_data, address_data, patient_data):
        user_instance = patient.user
        address_instance = patient.address

        username = user_data.get("username")
        cpf = user_data.get("cpf")

        if username and CustomUser.objects.exclude(pk=user_instance.pk).filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username já cadastrado por outro usuário"})

        if cpf and CustomUser.objects.exclude(pk=user_instance.pk).filter(cpf=cpf).exists():
            raise serializers.ValidationError({"cpf": "CPF já cadastrado por outro usuário"})

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
    
