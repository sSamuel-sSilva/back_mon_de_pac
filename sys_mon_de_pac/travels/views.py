from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .services import TravelBookingService

from .models import *
from users.models import Card, Patient
from .serializers import *
from .filters import TravelBookingFilter

class BusViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Bus.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return BusListRetrieveSerializer
        return BusCreateUpdateDeleteSerializer 


class DestinyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Destiny.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return DestinyListRetrieveSerializer
        return DestinyCreateUpdateDeleteSerializer 


class TravelViewSet(viewsets.ModelViewSet):
    queryset = Travel.objects.all() 

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [p() for p in permission_classes]


    def get_serializer_class(self):
        if self.action == 'list':
            return TravelListSerializer

        if self.action == 'retrieve':
            return TravelRetrieveSerializer

        return TravelCreateUpdateDeleteSerializer


    #URL = /travels/travel/{id}/change_travel_status/
    @action(detail=True, methods=["patch", "put"])
    def change_travel_status(self, request, pk=None):
        serializer = ChangeTravelStatusSerializer(instance=self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        travel = self.get_object()
        t_serializer = TravelRetrieveSerializer(travel)
        return Response(t_serializer.data)
        

    #URL = /travels/travel/get_all_pendents/
    @action(detail=False, methods=["get"])
    def get_pendents(self, request, pk=None):
        qs = self.get_queryset().filter(status=0)
        serializer = AdminTravelPendentsSerializer(qs, many=True)
        return Response(serializer.data)

    
    #URL = /travels/travel/{id}/get_bookigns_by_travel/
    @action(detail=True, methods=["get"])
    def get_bookigns_by_travel(self, request, pk):
        qs = TravelBooking.objects.filter(travel=pk)
        serializer = AdminTravelBookingSerializer(qs, many=True)
        return Response(serializer.data)


class TravelBookingViewSet(viewsets.ModelViewSet):
    queryset = queryset = TravelBooking.objects.all()
    filterset_class = TravelBookingFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return TravelBooking.objects.all()
        else:
            return TravelBooking.objects.filter(patient__user=user)


    def get_permissions(self):
        if self.action in ['post_travel_booking', 'change_travel_booking_status', 'list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [p() for p in permission_classes]


    def get_serializer_class(self):
        if self.action == 'list':
            return TravelBookingListSerializer

        if self.action == 'retrieve':
            return TravelBookingRetrieveSerilizer

        return TravelBookingCreateUpdateDeleteSerializer


    #URL = /travels/travel_booking/get_travel_booking/
    @action(detail=False, methods=["get"])
    def get_all_travel_booking(self, request, pk=None):
        t = self.get_queryset()
        serializer = AdminTravelBookingSerializer(t, many=True)
        return Response(serializer.data)


    # #URL = /travels/travel_booking/get_travel_booking_travel/?travel_id={id}/
    # @action(detail=False, methods=["get"])
    # def get_travel_booking_travel(self, request, pk=None):
    #     travel_id = request.GET.get("travel_id")
            
    #     qs = self.get_queryset().filter(travel=travel_id, status=0)
    #     serializer = AdminTravelBookingSerializer(qs, many=True)
    #     return Response(serializer.data)


    #URL = /travels/travel_booking/post_travel_booking/
    @action(detail=False, methods=["post"])
    def post_travel_booking(self, request):
        travel_id = request.data.get("travel_id")
        patient_id = request.data.get("patient_id")
        companion_id = request.data.get("companion_id")

        booking = TravelBookingService.create_booking(
            travel_id=travel_id,
            patient_id=patient_id,
            companion_id=companion_id,
            request=request)

        serializer = TravelBookingCreateUpdateDeleteSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    #URL = /travels/travel_booking/change_travel_booking_status/{id}/
    @action(detail=True, methods=["put", "patch"])
    def change_travel_booking_status(self, request, pk):
        TravelBookingService.toogle_status(self.get_object(), request)

        serializer = TravelBookingRetrieveSerilizer(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=False, methods=["get"])
    def get_bookigns_by_travel_app(self, request):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        serializer = TravelBookingUserInfo(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 
        

class BoardingRecordViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthetication]
    permission_classes = [AllowAny] # por hora vai ficar assim, depois tenho que fazer um esquema de autenticação para a placa ou então verificação por código
    queryset = Travel.objects.all()

    # def get_permissions(self):
    #     if self.action in ['create']
    #         return [IsAuthenticated()] # depois tem q ver o esquema de autenticação na placa
        
    #     return return [ActionPermission()]


    def get_serializer_class(self):
        if self.action == 'list':
            return BoardingRecordListSerializer

        if self.action == 'retrieve':
            return TravelBookingRetrieveSerilizer

        return BoardingRecordCreateUpdateDelete

    #URL = /travels/board_record/create_record/
    @action(detail=False, methods=["post"])
    def create_record(self, request):
        travel_booking_id = request.data.get('travel_booking_id')
        uid_card = request.data.get('uid_card')
        bus_id = request.data.get('bus_id')

        record = BoardingRecordService.create_booking(travel_booking_id, uid_card, bus_id)
        serializer = BoardingRecordCreateUpdateDelete(record)

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
                    'time': current_boarding_record.time
                }
            }
        )

        return Response(serializer.data, status=status.HTTP_200_OK)