# from django.db.models import F
# from rest_framework.exceptions import ValidationError as DRFValidationError
# from rest_framework.exceptions import NotFound as DRFNotFound
# from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
# from .serializers import TravelBookingServicePostTravelBooking, ChangeTravelBookingStatus

from django.db import transaction
from sys_mon_de_pac.travels.serializers import TravelBookingReadSerializer, TravelBookingWriteSerializer
from .models import *
from users.models import Patient, VitalMonitorDevice
from rest_framework import serializers
from datetime import datetime, timedelta
from django.utils import timezone


class TravelBookingService:
    @staticmethod
    @transaction.atomic
    def create(request, data):
        data["status"] = 0

        patient = data.get("patient")
        travel = data.get("travel")
        companion = data.get("companion")

        travel = Travel.objects.select_for_update().get(pk=travel.pk)

        if  (patient.user != request.user) and (not request.user.is_staff):
            raise serializers.ValidationError("Usuário não tem permissão para realizar a operação.")
        
        if travel.status != 0:
            raise serializers.ValidationError("Solicitação inválida: Viagem não está mais pendente.")
        
        travel_datetime = timezone.make_aware(
            datetime.combine(travel.date, travel.time),
            timezone.get_current_timezone()
        )
        limit = travel_datetime - timedelta(hours=2)
        if timezone.now() > limit:
            raise serializers.ValidationError("O prazo para solicitações já expirou.")
        
        needed = 2 if companion else 1
        if travel.vacations >= needed:
            # caso tenha vagas suficientes, prepara o terreno
            data = TravelBookingService.confirm_booking(data, needed)
        
        return TravelBooking.objects.create(**data)
    

    @staticmethod
    def update(request, instance, data):
        patient = instance.patient

        if  (patient.user != request.user) and (not request.user.is_staff):
            raise serializers.ValidationError("Usuário não tem permissão para realizar a operação.")
        
        fields = ["need_vital_monitor_device", "observations"]
        if (request.user.is_staff):
            fields.extend(["travel", "card", "vital_monitor_device"]) 

        for field, value in data.items():
            if field in fields:
                setattr(instance, field, value)
        
        instance.save()


    @staticmethod
    @transaction.atomic
    def cancelBooking(request, instance, reason):
        patient = instance.patient

        if  (patient.user != request.user) and (not request.user.is_staff):
            raise serializers.ValidationError("Usuário não tem permissão para realizar a operação.")

        if instance.status == 1:
            raise serializers.ValidationError("Não é possível cancelar uma solicitação que já está cancelada.")
        
        travel = Travel.objects.select_for_update().get(travel=instance.travel)
        if instance.status == 2:
            total_vacations = 2 if instance.companion else 1
            travel.vacations += total_vacations
        
            if instance.card:
                Card.objects.filter(pk=instance.card_id).update(in_use=False)
            if instance.vital_monitor_device:
                VitalMonitorDevice.objects.filter(pk=instance.vital_monitor_device_id).update(in_use=False)

        instance.status = 1
        instance.card = None
        instance.vital_monitor_device = None
        instance.save()

        next_inline = TravelBooking.objects.filter(travel=travel, status=0).order_by('created_at').first()

        if next_inline:
            needed_next = 2 if next_inline.companion else 1
            if travel.vacations >= needed_next:
                
                card = Card.objects.select_for_update().filter(in_use=False).first()
                if card:
                    next_inline.card = card
                    card.in_use = True
                    card.save()
                    
                    if next_inline.need_vital_monitor_device:
                        dev = VitalMonitorDevice.objects.select_for_update().filter(in_use=False).first()
                        if dev:
                            next_inline.vital_monitor_device = dev
                            dev.in_use = True
                            dev.save()
                    
                    travel.vacations -= needed_next
                    next_inline.status = 2
                    next_inline.save()

        travel.save()

        return CancelTravelBookingTicket.objects.create(user=request.user, travel=travel, reason=reason)


    @staticmethod
    @transaction.atomic
    def confirm_booking(data, needed):
        travel = data.get("travel")
        travel = Travel.objects.select_for_update().get(travel=travel)


        card = Card.objects.select_for_update().filter(in_use=False).first()
        if not card:
            raise serializers.ValidationError("Sem cartões disponíveis.")
        
        device = None
        if data.get("need_vital_monitor_device"):
            device = VitalMonitorDevice.objects.select_for_update().filter(in_use=False).first()
            if not device:
                raise serializers.ValidationError("Sem dispositivos.")

        travel.vacations -= needed
        travel.save()

        card.in_use = True
        card.save()
        
        if device:
            data["vital_monitor_device"] = device
            device.in_use = True
            device.save()

        data["card"] = card
        data["status"] = 2

        return data
    

class TravelService:
    pass

# implementar o cancelamento da viagem
# só uma viagem ainda pendente pode ser cancelada
# todos as solicitações, independente do status, serão canceladas
