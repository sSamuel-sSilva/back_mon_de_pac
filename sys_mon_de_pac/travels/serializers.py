from rest_framework import serializers
from users.serializers import PatientListRetrieveSerializer, CompanionListRetrieveSerializer
from. models import *
from users.models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
 

class BusListRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ['id', 'identifier_code']


class BusCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ['identifier_code']


# ===========================================================DestinySerializers===============================================


class DestinyListRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destiny
        fields = ['id', 'destiny']


class DestinyCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destiny
        fields = ['destiny']


# ===========================================================TravelSerializers===============================================
class TravelListSerializer(serializers.ModelSerializer):
    travel_str = serializers.SerializerMethodField()
    qtd_patients = serializers.SerializerMethodField()
    qtd_bookings = serializers.SerializerMethodField()
    destiny = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True
    )

    class Meta:
        model = Travel
        fields = ['id', 'travel_str', 'destiny', 'date', 'time', 'vacations', 'qtd_patients', 'qtd_bookings', 'status', 'status_label']

    def get_travel_str(self, obj):
        return obj.__str__()

    def get_qtd_patients(self, obj):
        return TravelBooking.objects.filter(travel=obj, status=2).count()

    def get_qtd_bookings(self, obj):
        return TravelBooking.objects.filter(travel=obj, status=0).count()

    def get_destiny(self, obj):
        return obj.destiny.__str__()

    def get_date(self, obj):
        date = obj.date.strftime("%d/%m/%Y")
        return date


class TravelRetrieveSerializer(serializers.ModelSerializer):
    travel_str = serializers.SerializerMethodField()
    qtd_patients = serializers.SerializerMethodField()
    qtd_bookings = serializers.SerializerMethodField()
    status = serializers.IntegerField()
    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True
    )

    owner = serializers.SerializerMethodField()
    monitor = serializers.SerializerMethodField()
    driver = serializers.SerializerMethodField()
    destiny = serializers.SerializerMethodField()
    bus = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = Travel
        fields = ['id', 'travel_str', 'owner', 'monitor', 'driver', 'destiny', 'bus', 'vacations', 'qtd_patients', 'qtd_bookings', 'date', 'time', 'status', 'status_label']

    def get_travel_str(self, obj):
        return obj.__str__()

    def get_owner(self, obj):
        return obj.owner.__str__()

    def get_monitor(self, obj):
        return obj.monitor.__str__()

    def get_driver(self, obj):
        return obj.driver.__str__()

    def get_destiny(self, obj):
        return obj.destiny.__str__()

    def get_bus(self, obj):
        return obj.bus.__str__()

    def get_qtd_patients(self, obj):
        return TravelBooking.objects.filter(travel=obj, status=2).count()

    def get_qtd_bookings(self, obj):
        return TravelBooking.objects.filter(travel=obj, status=0).count()

    def get_date(self, obj):
        date = obj.date.strftime("%d/%m/%Y")
        return date


class TravelCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travel
        fields = ['id', 'owner', 'monitor', 'driver', 'destiny', 'vacations', 'bus', 'date', 'time', 'status']


class ChangeTravelStatusSerializer(serializers.ModelSerializer):
    status = serializers.IntegerField()

    class Meta:
        model = Travel
        fields = ['status']


# =========================================================TravelBookingSerializers===============================================
class TravelBookingListSerializer(serializers.ModelSerializer):
    travel = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()
    companion = serializers.SerializerMethodField()

    class Meta:
        model = TravelBooking
        fields = ['id', 'travel', 'patient', 'companion', 'date', 'time', 'status']

    def get_travel(self, obj):
        return obj.travel.__str__()

    def get_patient(self, obj):
        return obj.patient.__str__()

    def get_companion(self, obj):
        return obj.companion is not None


class TravelBookingRetrieveSerilizer(serializers.ModelSerializer):
    status = serializers.IntegerField()
    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True
    )
    
    travel = TravelRetrieveSerializer()
    patient = PatientListRetrieveSerializer()
    companion = CompanionListRetrieveSerializer()

    class Meta:
        model = TravelBooking
        fields = ['id', 'travel', 'patient', 'companion', 'date', 'time', 'status_label', 'status']


class TravelBookingCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelBooking
        fields = ['id', 'travel', 'patient', 'companion', 'date', 'time', 'status']


class TravelBookingServicePostTravelBooking(serializers.Serializer):
    travel_id = serializers.IntegerField(required=True)
    patient_id = serializers.IntegerField(required=True)
    companion_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        try:
            travel = Travel.objects.get(pk=data["travel_id"])
        except Travel.DoesNotExist:
            raise ValidationError({"travel_id": "Viagem não encontrada."})

        try:
            patient = Patient.objects.get(pk=data["patient_id"])
        except Patient.DoesNotExist:
            raise ValidationError({"patient_id": "Paciente não encontrado."})

        companion = None
        if data.get("companion_id"):
            try:
                companion = Companion.objects.get(pk=data["companion_id"])
            except Companion.DoesNotExist:
                raise ValidationError({"companion_id": "Acompanhante não encontrado."})

        data["travel"] = travel
        data["patient"] = patient
        data["companion"] = companion
    
        return data


class ChangeTravelBookingStatus(serializers.Serializer):
    status = serializers.IntegerField(min_value=0, max_value=2)


class TravelBookingUserInfo(serializers.ModelSerializer):
    patient_id = serializers.CharField(source='patient.id')
    patient_name = serializers.CharField(source='patient.name')
    patient_number =serializers.SerializerMethodField()
    date_booking = serializers.SerializerMethodField()
    time_booking = serializers.SerializerMethodField()
    card = serializers.SerializerMethodField()
    has_companion = serializers.SerializerMethodField()

    status_label = serializers.CharField(
        source="get_status_display",
        read_only=True
    )

    class Meta:
        model = TravelBooking
        fields = ['id', 'patient_id', 'patient_name', 'patient_number', 'card', 'status', 'status_label', 'date_booking', 'time_booking', 'has_companion']


    def get_card(self, obj):
        return obj.card.__str__()

    def get_has_companion(self, obj):
        return obj.companion != None

    def get_date_booking(self, obj):
        date = obj.date.strftime("%d/%m/%Y")
        return date

    def get_time_booking(self, obj):
        time = obj.time.strftime("%H:%M")
        return time

    def get_patient_number(self, obj):
        tel = obj.patient.telephone
        return f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"

    
class CompanionByTravel(serializers.ModelSerializer):
    id = serializers.IntegerField(source='companion.id')
    patient_id = serializers.IntegerField(source='patient.id')
    name = serializers.CharField(source='companion.name')
    telephone = serializers.CharField(source='companion.telephone')

    class Meta:
        model = TravelBooking
        fields = ['id', 'patient_id', 'name', 'telephone']


class PatientByTravel(serializers.ModelSerializer):
    id = serializers.IntegerField(source="patient.id")
    name = serializers.CharField(source="patient.name")
    telephone = serializers.CharField(source="patient.telephone")
    cep = serializers.CharField(source="patient.address.cep")
    street = serializers.CharField(source="patient.address.street")
    number = serializers.CharField(source="patient.address.number")
    city = serializers.CharField(source="patient.address.city")
    state = serializers.CharField(source="patient.address.state")
    complement = serializers.CharField(source="patient.address.complement")
    neighborhood = serializers.CharField(source="patient.address.neighborhood")

    class Meta:
        model = TravelBooking
        fields = ['id', 'name', 'telephone', 'cep', 'street', 'number', 'city', 'state', 'complement', 'neighborhood']


# =========================================================BoardingRecordSerializers===============================================
class BoardingRecordListSerializer(serializers.ModelSerializer):
    travel_booking = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()

    class Meta:
        model = BoardingRecord
        fields = ['id', 'travel_booking', 'patient', 'card', 'bus', 'on_board', 'created_at']

    def get_travel_booking(self, obj):
        return obj.travel_booking.__str__()

    def get_travel_booking(self, obj):
        return obj.patient.__str__()


class BoardingRecordRetrieveSerializer(serializers.ModelSerializer):
    travel_booking = TravelBookingRetrieveSerilizer(source='travel_booking')
    patient = PatientListRetrieveSerializer(source='patient')

    class Meta:
        model = BoardingRecord
        fields = ['id', 'travel_booking', 'patient', 'card', 'bus', 'on_board', 'created_at']


class BoardingRecordCreateUpdateDelete(serializers.ModelSerializer):
    class Meta:
        model = BoardingRecord
        fields = ['id', 'travel_booking', 'patient', 'card', 'bus', 'on_board', 'created_at']


# ============================================================CustomizedSerializers================================================
class AdminTravelBookingSerializer(serializers.ModelSerializer):
    travel_id = serializers.IntegerField(source='travel.id', read_only=True)
    patient_id = serializers.IntegerField(source='patient.id', read_only=True)
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    patient_number = serializers.CharField(source='patient.telephone', read_only=True)
    patient_address = serializers.CharField(source='patient.address', read_only=True)
    travel_destiny = serializers.CharField(source='travel.destiny', read_only=True)
    travel_vacations = serializers.IntegerField(source='travel.vacations', read_only=True)
    patient_complement = serializers.SerializerMethodField()

    class Meta:
        model = TravelBooking
        # Adicionamos 'id', 'travel_id' e 'patient_id' aqui:
        fields = [
            'id', 'travel_id', 'patient_id', 'patient_name', 'patient_number', 
            'patient_address', 'patient_complement', 'travel_vacations', 
            'companion', 'status', 'travel_destiny', 'date', 'time'
        ]

    def get_patient_complement(self, obj):
        try:
            return obj.patient.user.address.complement
        except AttributeError:
            return ""


class AdminTravelPendentsSerializer(serializers.ModelSerializer):
    travel_id = serializers.SerializerMethodField()
    travel_name = serializers.SerializerMethodField()


    class Meta:
        model = Travel
        fields = ['id', 'travel_id', 'travel_name']


    def get_travel_name(self, obj):
        return obj.__str__()

    def get_travel_id(self, obj):
        return obj.id

