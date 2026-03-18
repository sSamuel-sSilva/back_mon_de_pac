from .models import Patient, Companion
from django.shortcuts import get_object_or_404


class PatientQuery:
    @staticmethod
    def get_patient_all(user):
        queryset = Patient.objects.all()

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        return [
            {
                "id": p.pk,
                "name": p.name,
                "telephone": p.telephone,
                "user": {
                    "id": p.user.pk,
                    "username": p.user.username,
                    "cpf": p.user.cpf
                },
                "address": {
                    "id": p.address.pk,
                    "city": p.address.city,
                    "state": p.address.state
                }
            }
            for p in queryset
        ]


    @staticmethod
    def get_patient_detail(user, p_id):
        queryset = Patient.objects.select_related("user", "address")
        if not user.is_staff:
            queryset = queryset.filter(user=user)
        
        p = get_object_or_404(queryset, id=p_id)

        return {
            "id": p.pk,
            "name": p.name,
            "telephone": p.telephone,
            "user": {
                "id": p.user.pk,
                "username": p.user.username,
                "cpf": p.user.cpf,
            },
            "address": {
                "id": p.address.pk,
                "cep": p.address.cep,
                "street": p.address.street,
                "number": p.address.number,
                "city": p.address.city,
                "state": p.address.state,
                "complement": p.address.complement,
                "neighborhood": p.address.neighborhood
            }
        }


class CompanionQuery:
    @staticmethod
    def get_companion_s(user, many=False, pk=None):
        queryset = Companion.objects.all()

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        if many:
            return [
                {
                    "id": c.pk, 
                    "name": c.name,
                    "telephone": c.telephone,
                    "user": {
                        "id": c.user.pk,
                        "name": getattr(c.user, "patient", None) and c.user.patient.name,
                    }
                } for c in queryset
            ]
        
        if pk:
            c = get_object_or_404(queryset, id=pk)
            return  {
                    "id": c.pk, 
                    "name": c.name,
                    "telephone": c.telephone,
                    "user": {
                        "id": c.user.pk,
                        "name": getattr(c.user, "patient", None) and c.user.patient.name,
                    }
                } 
        

