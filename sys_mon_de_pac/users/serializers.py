from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Address, Card, Companion, CustomUser, Patient, VitalMonitorDevice


class CustomUserWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["username", "password", "is_staff", "cpf", "type"]


    def _can_assign_privileged_type(self, requested_type):
        if requested_type not in [CustomUser.UserType.ADMIN, CustomUser.UserType.MONITOR]:
            return True

        request = self.context.get("request")
        return bool(request and request.user and request.user.is_superuser)


    def create(self, validated_data):
        password = validated_data.pop("password")
        requested_type = validated_data.pop("type", CustomUser.UserType.PACIENTE)

        if not self._can_assign_privileged_type(requested_type):
            raise serializers.ValidationError({"type": "Sem permissão para atribuir tipo privilegiado."})

        user = CustomUser(type=requested_type, **validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        requested_type = validated_data.pop("type", None)

        if requested_type is not None:
            if not self._can_assign_privileged_type(requested_type):
                raise serializers.ValidationError({"type": "Sem permissão para atribuir tipo privilegiado."})
            instance.type = requested_type

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance

    
class CustomUserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "cpf", "type"]
        read_only_fields = fields


class AddressWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["cep", "street", "number", "city", "state", "complement", "neighborhood"]


class AddressReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "user", "cep", "street", "number", "city", "state", "complement", "neighborhood"]
        read_only_fields = fields


class PatientWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["name", "telephone"]


class CompanionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companion
        fields = ["user", "name", "telephone"]


class CompanionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Companion
        fields = ["id", "user", "name", "telephone"]
        read_only_fields = fields


class CardWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ["uid", "in_use"]

class CardReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ["id", "uid", "in_use"]
        read_only_fields = fields


class VitalMonitorDeviceWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalMonitorDevice
        fields = ["code", "in_use"]

class VitalMonitorDeviceReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalMonitorDevice
        fields = ["id", "code", "in_use"]
        read_only_fields = fields


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['type'] = self.user.type

        return data
