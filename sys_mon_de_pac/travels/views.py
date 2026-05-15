from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action, api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from asgiref.sync import async_to_sync

from sys_mon_de_pac.travels.queries import TravelBookingQuery, TravelQuery
from .services import TravelBookingService
from .models import *
from users.models import Card, Patient
from .serializers import *
from .filters import TravelBookingFilter
from users.permissions import CustomPermission

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

    
class BusViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Bus.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return BusReadSerializer
        return BusWriteSerializer 


class DestinyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Destiny.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return DestinyReadSerializer
        return DestinyWriteSerializer 


class TravelViewSet(viewsets.ModelViewSet):
    queryset = Travel.objects.all() 

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [p() for p in permission_classes]


    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TravelReadSerializer
        return TravelReadSerializer


    @action(detail=True, methods=["get"])
    def get_bookings_by_travel(self, reqeust, pk=None):
        data = TravelQuery.get_bookings_by_travel(self.request.user, pk)
        if not data:
            return Response({"detail": "Not found."}, status=404)
        return Response(data)

#     #URL = /travels/travel/{id}/change_travel_status/
#     @action(detail=True, methods=["patch", "put"])
#     def change_travel_status(self, request, pk=None):
#         serializer = ChangeTravelStatusSerializer(instance=self.get_object(), data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         travel = self.get_object()
#         t_serializer = TravelRetrieveSerializer(travel)
#         return Response(t_serializer.data)
        

#     #URL = /travels/travel/get_all_pendents/
#     @action(detail=False, methods=["get"])
#     def get_pendents(self, request, pk=None):
#         qs = self.get_queryset().filter(status=0)
#         serializer = AdminTravelPendentsSerializer(qs, many=True)
#         return Response(serializer.data)

    
#     #URL = /travels/travel/{id}/get_bookigns_by_travel/
#     @action(detail=True, methods=["get"])
#     def get_bookigns_by_travel(self, request, pk):
#         qs = TravelBooking.objects.filter(travel=pk)
#         serializer = AdminTravelBookingSerializer(qs, many=True)
#         return Response(serializer.data)

# pegar os bookings a partir de travel
# pegar os pacientes que estão na viagem
# pegar acompanhantes a apartir da viagem


class TravelBookingViewSet(viewsets.ModelViewSet):
    queryset = queryset = TravelBooking.objects.all()
    # filterset_class = TravelBookingFilter

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return TravelBooking.objects.all()
        else:
            return TravelBooking.objects.filter(patient__user=user)


    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [CustomPermission]
        return [p() for p in permission_classes]


    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TravelBookingReadSerializer
        return TravelBookingWriteSerializer


    def list(self, request, *args, **kwargs):
        data = TravelBookingQuery.get_travel_booking_all(request.user)
        return Response(data)

    
    def retrieve(self, request, pk=None, *args, **kwargs):
        data = TravelBookingQuery.get_travel_booking_detail(request.user, pk)
        if not data:
            return Response({"detail": "Not found."}, status=404)
        return Response(data)


    def create(self, request, *args, **kwargs):
        booking = TravelBookingService.create_booking(request.data, request)
        serializer = TravelBookingReadSerializer(booking)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def update(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        booking = TravelBookingService.update_booking(instance, request.data, request)
        serializer = TravelBookingReadSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def cancel_booking(self, request, pk=None):
        instance = self.get_object()
        reason = request.data.get("reason", "")
        cancel = TravelBookingService.cancel_booking(instance, reason, request)
        serializer = CancelTravelBookingTicketSerializer(cancel)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class BoardingRecordViewSet(viewsets.ModelViewSet):
#     # authentication_classes = [JWTAuthetication]
#     permission_classes = [AllowAny] # por hora vai ficar assim, depois tenho que fazer um esquema de autenticação para a placa ou então verificação por código
#     queryset = Travel.objects.all()

#     # def get_permissions(self):
#     #     if self.action in ['create']
#     #         return [IsAuthenticated()] # depois tem q ver o esquema de autenticação na placa
        
#     #     return return [ActionPermission()]


#     def get_serializer_class(self):
#         if self.action == 'list':
#             return BoardingRecordListSerializer

#         if self.action == 'retrieve':
#             return TravelBookingRetrieveSerilizer

#         return BoardingRecordCreateUpdateDelete

#     #URL = /travels/board_record/create_record/
#     @action(detail=False, methods=["post"])
#     def create_record(self, request):
#         travel_booking_id = request.data.get('travel_booking_id')
#         uid_card = request.data.get('uid_card')
#         bus_id = request.data.get('bus_id')

#         record = BoardingRecordService.create_booking(travel_booking_id, uid_card, bus_id)
#         serializer = BoardingRecordCreateUpdateDelete(record)

#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             'cards_monitor',
#             {
#                 'type': 'send_event',
#                 'event': {
#                     'name': current_boarding_record.patient.name,
#                     'number': current_boarding_record.patient.telephone,
#                     'on_board':current_boarding_record.on_board,
#                     'uid': current_boarding_record.card.uid,
#                     'time': current_boarding_record.time
#                 }
#             }
#         )

#         return Response(serializer.data, status=status.HTTP_200_OK)