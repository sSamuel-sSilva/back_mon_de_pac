from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from sys_mon_de_pac.users.permission import CustomPermission
from .models import *
from .serializers import *
from .services import *
from .queries import *


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CustomUserReadSerializer
        return CustomUserWriteSerializer

    @action(detail=False, methods=["get"], permission_classes=[AllowAny], authentication_classes=[])
    def test_connection(self, request):
        return Response(status=status.HTTP_200_OK)
        
    

class PatientViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [CustomPermission]

        return [permission() for permission in permission_classes]
    

    def list(self, request, *args, **kwargs):
        data = PatientQuery.get_patient_all(request.user)
        return Response(data)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        data = PatientQuery.get_patient_detail(request.user, pk)
        if not data:
            return Response({"detail": "Not found."}, status=404)
        return Response(data)
    
    def create(self, request, *args, **kwargs):
        user_serializer = CustomUserWriteSerializer(data=request.data["user"])
        user_serializer.is_valid(raise_exception=True)

        address_serializer = AddressWriteSerializer(data=request.data["address"])
        address_serializer.is_valid(raise_exception=True)        

        patient_serializer = PatientWriteSerializer(data=request.data["patient"])
        patient_serializer.is_valid(raise_exception=True)

        patient = PatientCreateService.create(
            user_serializer.validated_data,
            address_serializer.validated_data,
            patient_serializer.validated_data)
        
        res = PatientQuery.get_patient_detail(request.user, patient.pk)
        return Response(status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        patient = Patient.objects.get(pk=pk)

        user_serializer = CustomUserWriteSerializer(
            instance=patient.user,
            data=request.data.get("user", {}),
            partial=True
        )
        user_serializer.is_valid(raise_exception=True)

        address_serializer = AddressWriteSerializer(
            instance=patient.address,
            data=request.data.get("address", {}),
            partial=True
        )
        address_serializer.is_valid(raise_exception=True)

        patient_serializer = PatientWriteSerializer(
            instance=patient,
            data=request.data.get("patient", {}),
            partial=True
        )
        patient_serializer.is_valid(raise_exception=True)

        patient = PatientUpdateService.update(
            patient,
            user_serializer.validated_data,
            address_serializer.validated_data,
            patient_serializer.validated_data
        )

        res = PatientQuery.get_patient_detail(request.user, pk)
        return Response(res, status=status.HTTP_200_OK)

        
    
class CompanionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Companion.objects.all()
    permission_classes = [CustomPermission]

    def list(self, request, *args, **kwargs):
        data = CompanionQuery.get_companion_s(request.user, many=True)
        return Response(data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        data = CompanionQuery.get_companion_s(request.user, pk=pk)
        if not data:
            return Response({"detail": "Not found."}, status=404)
        return Response(data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return CompanionWriteSerializer


class CardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Card.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CardReadSerializer
        return CardWriteSerializer  
