from rest_framework import serializers
from .models import *


class CustomUserCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'cpf', 'type']


class CustomUserListRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'cpf', 'type']
        read_only_fields = ['id', 'username', 'email', 'cpf', 'type']


class AddressCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['user', 'cep', 'street', 'number', 'city', 'state', 'complement', 'neighborhood']


class AddressListRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'cep', 'street', 'number', 'city', 'state', 'complement', 'neighborhood']
        read_only_fields = ['id', 'user', 'cep', 'street', 'number', 'city', 'state', 'complement', 'neighborhood']


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['user', 'address', 'name', 'telephone']

    def get_endereco(self, obj):
        return obj.address.__str__()
 

class PatientCreateUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=False)
    password = serializers.CharField(write_only=True, min_length=8, required=False)
    cpf = serializers.CharField(max_length=11, required=False)
    
    name = serializers.CharField(max_length=255, required=False)
    telephone = serializers.CharField(max_length=11, required=False)

    cep = serializers.CharField(max_length=10, allow_blank=True, required=False)
    street = serializers.CharField(max_length=100, required=False)
    number = serializers.CharField(max_length=10, required=False)
    city = serializers.CharField(max_length=50, required=False)
    state = serializers.CharField(max_length=50, required=False)
    complement = serializers.CharField(max_length=128, allow_blank=True, required=False)
    neighborhood = serializers.CharField(max_length=128, required=False)


    def validate(self, data):
        user_instance = getattr(self.instance, 'user', None)

        if 'cpf' in data:
            qs = CustomUser.objects.filter(cpf=data['cpf'])
            if user_instance:
                qs = qs.exclude(id=user_instance.id)
            if qs.exists():
                raise serializers.ValidationError({"cpf": "CPF já cadastrado por outro usuário"})

        if 'username' in data:
            qs = CustomUser.objects.filter(username=data['username'])
            if user_instance:
                qs = qs.exclude(id=user_instance.id)
            if qs.exists():
                raise serializers.ValidationError({"username": "Username já cadastrado por outro usuário"})

        if 'telephone' in data:
            if not data['telephone'].isdigit() or len(data['telephone']) not in [10, 11]:
                raise serializers.ValidationError({"telephone": "Telefone inválido"})

        if 'cep' in data and data['cep'] and not data['cep'].isdigit():
            raise serializers.ValidationError({"cep": "CEP inválido"})

        return data


class PatientListRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'user', 'address', 'name', 'telephone']
        read_only_fields = ['id', 'user', 'address', 'name', 'telephone']


class CompanionCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companion
        fields = ['name', 'telephone'] 


class CompanionListRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companion
        fields = ['name', 'telephone']
        read_only_fields = ['name', 'telephone']


class CardCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['uid', 'in_use', 'patient']


class CardListRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'uid', 'in_use', 'patient']