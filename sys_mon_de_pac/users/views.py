from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action
from .models import *
from .serializers import *
from .services import PatientService


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return CustomUserListRetrieveSerializer
        return CustomUserCreateUpdateDeleteSerializer 
        

# class AddressViewSet(viewsets.ModelViewSet):
#     authentication_classes = [IsAuthenticated]
#     queryset = Address.objects.all()


#     def get_permissions(self):
#         if self.action == 'list':
#             permission_classes = [IsAdminUser]
#         else:
#             permission_classes = [IsAuthenticated]


#     def get_serializer_class(self):
#         if self.action == 'list' or self.action == 'retrieve':
#             return AddressListRetrieveSerializer
#         return AddressCreateUpdateDeleteSerializer
    

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Patient.objects.all()
        return Patient.objects.filter(user=user)


    def get_permissions(self):
        if self.action == 'create_patient':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]


    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return PatientListRetrieveSerializer
        return PatientSerializer


    @action(detail=False, methods=["post"])
    def create_patient(self, request):
        patient = PatientService.create_patient(request.data)
        serializer = PatientListRetrieveSerializer(patient)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=True, methods=["put", "partial_update"])
    def update_patient(self, request, pk):
        patient = PatientService.update_patient(self.get_object(), request.data)
        serializer = PatientListRetrieveSerializer(patient)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    
class CompanionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Companion.objects.all()

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return CompanionListRetrieveSerializer
        return CompanionCreateUpdateDeleteSerializer  


class CardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Card.objects.all()

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return CardListRetrieveSerializer
        return CardCreateUpdateDeleteSerializer  

# {
#   "username": "testano rota1",
#   "password": "12345678",
#   "cpf": "11111111111",
#   "name": "testa_da_silva_oliveira",
#   "telephone": "89665321540",
#   "cep": "65234185",
#   "street": "R de algum lugar dai em algum canto",
#   "number": "123456",
#   "city": "cidade_update",
#   "state": "estado_update",
#   "complement": "agr tem",
#   "neighborhood": "barro"
# }