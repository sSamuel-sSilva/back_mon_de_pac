from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import *
from .serializers import *
from .permissions import ActionPermission


class UserViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthetication]
    # permission_classes = [ActionPermission]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
        

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    # permission_classes = ActionPermission
    serializer_class = PatientSerializer


    # def get_authentication_classes(self):
    #     if self.action == 'create':
    #         return [] 

    def get_serializer_class(self):
        if self.action == 'list':
            return PatientViewSerializer
        return PatientSerializer   
    

class CardViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthentication]
    permission_classes = [ActionPermission]
    queryset = Card.objects.all()
    serializer_class = CardSerializer


    # def set_card_on_patient(self, request):
    #     """
    #     Função utilizada quando um administrador quer fazer o agendamento de uma pessoa.
    #     Usuários comuns não podem acessar essa função.
    #     """        

    #     patient_id = request.data['patient_id']
    #     card_uid = request.data['card_uid']

    #     if not patient_id or not card_uid:
    #         return Response({"error": "Usuário e/ou paciente não fornecido(s)."}, status=status.HTTP_400_BAD_REQUEST)
