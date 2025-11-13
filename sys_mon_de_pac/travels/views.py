from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import pytz
from datetime import datetime

from .models import *
from users.models import Card, Patient
from .serializers import *
from users.permissions import ActionPermission


tz = pytz.timezone("America/Sao_Paulo")


class BusViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthetication]
    permission_classes = [ActionPermission]
    queryset = Bus.objects.all()
    serializer_class = BusSerializer


class TravelViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthetication]
    queryset = Travel.objects.all()
    serializer_class = TravelSerializer
    permission_classes = [ActionPermission]

    #metodo para buscar lista de agendados
    #/travels/1/get_travel_booking/ jeito da url
    @action(detail=True, methods=["get"])
    def get_travel_booking(self, request, pk=None):
        travel = self.get_object()
        serializer = TravelTravelBooking(travel)

        return Response(serializer.data)
        

    #metodo para a lista dos que estão de fato no busao
    @action(detail=True, methods=["get"])
    def get_board_record(self, request, pk=None):
        travel = self.get_object()
        serializer = TravelBoardRecord(travel)

        return Response(serializer.data)
     

class TravelBookingViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthetication]
    queryset = queryset = Travel.objects.all()
    permission_classes = [ActionPermission]
    serializer_class = TravelBookingSerializer


    def toggle_confirmed(self, request): # por hora essa função vai ficar aqui, depois isolo ela em um service (ou não)
        if request.user.type in ['Paciente', 'Monitor', 'Admin']:
            travel_booking_id = request.data['travel_booking_id']
            patient_id = request.data['patient_id']

            if not patient_id:
                raise ValueError("Identificador do paciente não fornecido.")
            
            if not travel_booking_id:
                raise ValueError("Identificador do registro de agendamento não fornecido.")

            try:
                travel_booking = TravelBooking.objects.filter(id=travel_booking_id)
                travel_booking.confirmed = not travel_booking.confirmed                    
                travel_booking.save()

                # adicionar a lógica para dar um cartão ao o usuario
                patient = Patient.objects.get(id=patient_id)
                if not patient:
                    raise NotFound("Paciente não encontrado.")


                if travel_booking.confirmed: # da o cartão para o usuario se estiver confirmando
                    card = Card.objects.filter(in_use=False).first()
                    if not card:
                        raise NotFound("Sem cartões disponíveis.")
                        
                    card.set_card_on_patient(patient)

                else: # retira o cartão do usuario se estiver desconfirmando
                    card = Card.objects.filter(patient=patient).first()
                    card.release_card()
                    card.save()


            except TravelBooking.DoesNotExist:
                raise NotFound
            

            return Response({'success': 'Evento concluído com sucesso.'}, status=status.HTTP_200_OK) # ajustar esse texto de retorno
        
        else:
            raise PermissionDenied("Usuário não possui permissão para executar a ação.")
        
    
    def cancel_travel_booking(self, request): # talvez, cancelar pudesse ser apenas apagar o registro
        pass


class BoardingRecordViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthetication]
    queryset = queryset = Travel.objects.all()
    permission_classes = [AllowAny] # por hora vai ficar assim, depois tenho que fazer um esquema de autenticação para a placa ou então verificação por código
    serializer_class = BoardingRecordSerializer

    @action(detail=False, methods=["post"], url_path="send_record")
    def send_record(self, request):
        
        now = datetime.now(tz)
        formated_time_now = now.strftime("%H:%M:%S")

        travel_booking_id = request.data.get('travel_booking_id')
        uid_card = request.data.get('uid_card')
        bus_id = request.data.get('bus_id')


        current_boarding_record = BoardingRecord.objects.filter(travel_patient__id=travel_booking_id).order_by('-created_at').first()
        
        if not current_boarding_record:
            try:
                actual_travel_booking = TravelBooking.objects.get(id=travel_booking_id)

            except TravelBooking.DoesNotExist:
                raise ValidationError('Viagem inexistente.')

            try:
                actual_card = Card.objects.get(uid=uid_card)
            except Card.DoesNotExist:
                raise ValidationError('Cartão inexistente.')

            try:
                actual_bus = Bus.objects.get(id=bus_id)
            except Bus.DoesNotExist:
                raise ValidationError('Cartão inexistente.')
            
            current_boarding_record = BoardingRecord.objects.create(
                travel_patient=actual_travel_booking,
                patient=actual_travel_booking.patient,
                card=actual_card,
                bus=actual_bus
            )

        
        current_boarding_record.on_board = not current_boarding_record.on_board
        current_boarding_record.time = formated_time_now
        current_boarding_record.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'cards_monitor',
            {
                'type': 'send_event',
                'event': {
                    'name': current_boarding_record.patient.name,
                    'number': current_boarding_record.patient.telephone,
                    'on_board':current_boarding_record.on_board,
                    'uid': current_boarding_record.card.uid,
                    'time': formated_time_now
                }
            }
        )

        return Response({"detail": "evento de embarque processado com sucesso."}, status=status.HTTP_200_OK)