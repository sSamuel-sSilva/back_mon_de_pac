from django.db import transaction
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.exceptions import NotFound as DRFNotFound
from .serializers import PatientCreateUpdateSerializer
from .models import *

class PatientService:
    @staticmethod
    @transaction.atomic
    def create_patient(request_data):
        serializer = PatientCreateUpdateSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                username = data["username"],
                password = data["password"],
                cpf = data["cpf"],
                type='Paciente'
            )

            address = Address.objects.create(
                user = user,
                cep = data["cep"],
                street = data["street"],
                number = data["number"],
                city = data["city"],
                state = data["state"],
                complement = data["complement"],
                neighborhood = data["neighborhood"]
            )

            patient = Patient.objects.create(
                user = user,
                address = address,
                name = data["name"],
                telephone = data["telephone"]
            )

            return patient
    

    def update_patient(patient_instance, request_data):
        serializer = PatientCreateUpdateSerializer(
            instance=patient_instance,
            data=request_data,
            partial=True  
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = patient_instance.user
        address = patient_instance.address

        with transaction.atomic():
            if 'username' in data:
                user.username = data['username']
            if 'cpf' in data:
                user.cpf = data['cpf']
            if 'password' in data:                      # futuramente criar uma rota para isso, para poder fazer verificação por email
                user.set_password(data['password'])
            user.save()

            for field in ['cep', 'street', 'number', 'city', 'state', 'complement', 'neighborhood']:
                if field in data:
                    setattr(address, field, data[field])
            address.save()

            for field in ['name', 'telephone']:
                if field in data:
                    setattr(patient_instance, field, data[field])
            patient_instance.save()

        return patient_instance