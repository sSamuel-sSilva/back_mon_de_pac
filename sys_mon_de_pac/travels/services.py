from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.exceptions import NotFound as DRFNotFound
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import TravelBookingServicePostTravelBooking, ChangeTravelBookingStatus
from django.utils import timezone
from datetime import datetime, timedelta

class TravelBookingService:
    @staticmethod
    @transaction.atomic
    def create_booking(travel_id, patient_id, companion_id, request):
        serializer = TravelBookingServicePostTravelBooking(data={
            "travel_id": travel_id, 
            "patient_id": patient_id, 
            "companion_id": companion_id})

        serializer.is_valid(raise_exception=True)

        travel = serializer.validated_data["travel"]
        patient = serializer.validated_data["patient"]
        companion = serializer.validated_data["companion"]

        if (patient.user != request.user) and (not request.user.is_staff):
            raise DRFPermissionDenied("Usuário não tem permissão para realizar a operação.")


        if travel.status != 0:
            raise DRFValidationError("Viagem já em andamento.")

        travel_datetime = timezone.make_aware(
            datetime.combine(travel.date, travel.time)
        )
        limit = travel_datetime - timedelta(hours=2)
        if timezone.now() > limit:
            raise DRFValidationError("O prazo para solicitar vaga já expirou.")

        vagas_necessarias = 2 if companion else 1
        if travel.vacations < vagas_necessarias:
            raise DRFValidationError("Não há vagas suficientes.")

        booking = TravelBooking.objects.create(
            travel=travel,
            patient=patient,
            companion=companion,
            status=0
        )

        return booking


    @staticmethod
    @transaction.atomic
    def toogle_status(travel_booking, request):
        serializer = ChangeTravelBookingStatus(data=request.data)
        serializer.is_valid(raise_exception=True)

        patient = travel_booking.patient

        if request.user != patient.user and not request.user.is_staff:
            raise DRFPermissionDenied("Usuário não tem premissão para realizar a operação.")
        
        if serializer.validated_data["status"] == 2 and not request.user.is_staff:
            raise DRFPermissionDenied("Apenas administradores podem confirmar solicitações.")

        old_status = None
        old_status = travel_booking.status

        travel_booking.status = serializer.validated_data["status"]
        travel_booking.save()

        vac = 0
        # no caso de ta confirmando
        if (old_status == 0 and travel_booking.status == 2) or (not old_status and travel_booking.status == 2): 
            
            card = Card.objects.filter(in_use=False).first()
            if not card:
                raise DRFNotFound("Sem cartões disponíveis.")

            vac = -(2 if travel_booking.companion else 1)
            # card.set_card_on_patient(patient)
            card.set_use_as_true()
            travel_booking.card = card
            
                

        # no caso de ta cancelando
        elif old_status == 2 and travel_booking.status == 1 or (old_status == 2 and travel_booking.status == 0): 
            card = travel_booking.card
            card.release_card()
            travel_booking.card = null
            # card = Card.objects.filter(patient=patient).first()
            # card.release_card()
            vac = 2 if travel_booking.companion else 1
            

        if vac != 0:
            travel = travel_booking.travel
            Travel.objects.filter(pk=travel.pk).update(
                vacations=F('vacations') + vac
            )


class BoardingRecordService:
    def create_booking(travel_booking_id, uid_card, bus_id):
        current_travel_booking = get_object_or_404(TravelBooking, pk=travel_booking_id)
        current_card = get_object_or_404(Card, uid=uid_card)
        current_bus = get_object_or_404(Bus, pk=bus_id)
            
        current_boarding_record, created = BoardingRecord.objects.get_or_create (
            travel_booking=current_travel_booking,
            defaults={
                'patient': current_travel_booking.patient,
                'card': current_card,
                'bus': current_bus,
            }
        )

        current_boarding_record.on_board = not current_boarding_record.on_board

        now = datetime.now(tz)
        current_boarding_record.time = now().strftime("%H:%M:%S")
        current_boarding_record.save()

        return current_boarding_record
