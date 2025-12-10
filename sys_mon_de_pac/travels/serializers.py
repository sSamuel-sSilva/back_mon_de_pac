from rest_framework import serializers
from users.serializers import PatientViewSerializer, CompanionSerializer, AddressSerializer
from. models import *

class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        # fields = ['id', 'driver', 'monitor']
        fields = ['id', 'identifier_code']


class DestinySerializer(serializers.ModelSerializer):
    class Meta:
        models = Destiny
        fields = ['destiny']


# ===========================================================TravelSerializers===============================================
class TravelListSerializer(serializers.ModelSerializer):
    qtd_patients = serializers.SerializerMethodField()
    qtd_bookings = serializers.SerializerMethodField()
    destiny = serializers.CharField(source='destiny.destiny')

    class Meta:
        model = Travel
        fields = ['id', 'destiny', 'date', 'vacations', 'qtd_patients', 'qtd_bookings', 'status']


    def get_qtd_patients(self, obj):
        return len(TravelBooking.objects.filter(travel=obj, status='Confirmado'))


    def get_qtd_bookings(self, obj):
        return len(TravelBooking.objects.filter(travel=obj, status='Pendente'))


class TravelRetrieveSerializer(serializers.ModelSerializer):
    owner =     serializers.CharField(source='owner.username')
    monitor =   serializers.CharField(source='monitor.username')
    driver =    serializers.CharField(source='driver.username')
    destiny =   serializers.CharField(source='destiny.destiny')
    bus =       serializers.CharField(source='bus.identifier_code')

    class Meta:
        model = Travel
        fields = ['id', 'owner', 'monitor', 'driver', 'destiny', 'bus', 'vacations', 'date', 'time', 'status']


class TravelCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travel
        fields = ['id', 'owner', 'monitor', 'driver', 'destiny', 'bus', 'date', 'time', 'status']


# =========================================================TravelBookingSerializers===============================================
class TravelBookingListSerializer(serializers.ModelSerializer):
    travel = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()
    has_companion = serializers.SerializerMethodField()

    class Meta:
        model = TravelBooking
        fields = ['id', 'travel', 'patient', 'has_companion', 'date', 'time', 'status']

    def get_travel(self, obj):
        return obj.travel.__str__()

    def get_patient(self, obj):
        return obj.patient.__str__()

    def get_has_companion(self, obj):
        return obj.companion is not None


class TravelBookingRetrieveSerilizer(serializers.ModelSerializer):
    travel = TravelRetrieveSerializer()
    patient = PatientViewSerializer()
    companion = CompanionSerializer()

    class Meta:
        model = TravelBooking
        fields = ['id', 'travel', 'patient', 'companion', 'date', 'time', 'status']


class TravelBookingCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelBooking
        fields = ['id', 'travel', 'patient', 'companion', 'date', 'date', 'time', 'status']


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
    patient = PatientViewSerializer(source='patient')

    class Meta:
        model = BoardingRecord
        fields = ['id', 'travel_booking', 'patient', 'card', 'bus', 'on_board', 'created_at']


class BoardingRecordCreateUpdateDelete(serializers.ModelSerializer):
    class Meta:
        model = BoardingRecord
        fields = ['id', 'travel_booking', 'patient', 'card', 'bus', 'on_board', 'created_at']


# ============================================================CustomizedSerializers================================================
class AdminTravelBookingSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name')
    patient_number = serializers.CharField(source='patient.telephone')
    patient_address = serializers.CharField(source='patient.address')
    travel_destiny = serializers.CharField(source='travel.destiny')
    travel_vacations = serializers.CharField(source='travel.vacations')
    patient_complement = serializers.SerializerMethodField()


    class Meta:
        model = TravelBooking
        fields = ['patient_name', 'patient_number', 'patient_address', 'patient_complement', 'travel_vacations', 'companion' , 'status', 'travel_destiny', 'date', 'time']


    def get_patient_complement(self, obj):
        return obj.patient.user.address.complement


class AdminTravelPendentsSerializer(serializers.ModelSerializer):
    travel_name = serializers.SerializerMethodField()


    class Meta:
        model = Travel
        fields = ['id', 'travel_name']


    def get_travel_name(self, obj):
        return obj.__str__()



# class BoardingRecord2TravelBookingSerializer(serializers.ModelSerializer):
#     patient = serializers.CharField(source='patient.name')
#     telephone = serializers.CharField(source='patient.telephone')
#     companion = CompanionSerializer(source='travel_booking.companion')

#     class Meta:
#         model = BoardingRecord
#         fields = ['id', 'patient', 'telephone', 'companion', 'on_board']


# class TravelBoardRecord(serializers.ModelSerializer):
#     board_records = serializers.SerializerMethodField()

#     class Meta:
#         model = Travel
#         fields = ['id', 'owner', 'monitor', 'driver', 'destiny', 'bus', 'date', 'time', 'vacations', 'board_records']
    
    
#     def get_board_records(self, travel):
#         # pega todos os BoardingRecord cuja travel_patient.travel == travel
#         records_qs = BoardingRecord.objects.filter(
#             travel_patient__travel=travel
#         ).select_related('patient', 'card', 'bus', 'travel_patient')

#         return BoardingRecord2TravelBookingSerializer(records_qs, many=True).data


# class TravelBooking2TravelSerializer(serializers.ModelSerializer):
#     travelbooking_set = TravelBookingListSerializer(many=True, read_only=True)

#     class Meta:
#         model = Travel
#         fields = ['id', 'owner', 'monitor', 'driver', 'destiny', 'bus', 'date', 'time', 'travelbooking_set']


# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# class TravelBookingSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TravelBooking
#         fields = ['id', 'travel', 'patient', 'date', 'time', 'status']


# class BoardingRecordSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BoardingRecord
#         # fields = ['id', 'travel_patient', 'card', 'date', 'time', 'on_board']
#         fields = ['id', 'travel_patient', 'card', 'on_board']


# class TravelBookingSerializer2Nested(serializers.ModelSerializer):
#     class Meta:
#         model = TravelBooking
#         fields = ['id', 'patient', 'date', 'time', 'status']
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\



# class BoardRecordSerializer2Nested(serializers.ModelSerializer):
#     patient = serializers.CharField(source='patient.name')
#     telephone = serializers.CharField(source='patient.telephone')
#     companion = CompanionSerializer(source='travel_patient.companion')

#     class Meta:
#         model = BoardingRecord
#         fields = ['id', 'patient', 'telephone', 'companion', 'on_board']


# class TravelBoardRecord(serializers.ModelSerializer):
#     board_records = serializers.SerializerMethodField()

#     class Meta:
#         model = Travel
#         fields = ['id', 'owner', 'monitor', 'driver', 'destiny', 'bus', 'date', 'time', 'vacations', 'board_records']
    
    
#     def get_board_records(self, travel):
#         # pega todos os BoardingRecord cuja travel_patient.travel == travel
#         records_qs = BoardingRecord.objects.filter(
#             travel_patient__travel=travel
#         ).select_related('patient', 'card', 'bus', 'travel_patient')

#         return BoardRecordSerializer2Nested(records_qs, many=True).data
