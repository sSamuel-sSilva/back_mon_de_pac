from rest_framework import serializers
from .models import *

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'cpf', 'type']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'cep', 'street', 'number', 
                  'city', 'state', 'complement', 'neighborhood']


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'user', 'address', 'name', 'telephone']        


class PatientViewSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()
    cpf = serializers.CharField(source='user.cpf')

    class Meta:
        model = Patient
        fields = ['id', 'name', 'cpf', 'telephone', 'address']

    def get_address(self, obj):
        return obj.address.__str__()


class CompanionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companion
        fields = ['name', 'telephone'] 


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'uid', 'in_use', 'patient']