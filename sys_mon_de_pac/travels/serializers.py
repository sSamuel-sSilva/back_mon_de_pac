from rest_framework import serializers
from. models import *

class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ['id', 'driver', 'monitor']


class TravelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travel
        fields = ['owner', 'monitor', 'driver', 'bus', 'date', 'time']


class TravelBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelBooking
        fields = ['id', 'travel', 'patient', 'date', 'time', 'confirmed']


class BoardingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardingRecord
        # fields = ['id', 'travel_patient', 'card', 'date', 'time', 'on_board']
        fields = ['id', 'travel_patient', 'card', 'on_board']


class BoardRecordSerializer2Nested(serializers.ModelSerializer):
    patient = serializers.CharField(source='patient.name')
    telephone = serializers.CharField(source='patient.telephone')

    class Meta:
        model = BoardingRecord
        fields = ['id', 'patient', 'telephone', 'on_board']


class TravelBookingSerializer2Nested(serializers.ModelSerializer):
    class Meta:
        model = TravelBooking
        fields = ['id', 'patient', 'date', 'time', 'confirmed']


class TravelTravelBooking(serializers.ModelSerializer):
    bookings = TravelBookingSerializer2Nested(many=True, read_only=True)

    class Meta:
        model = Travel
        fields = ['id', 'owner', 'monitor', 'driver', 'bus', 'date', 'time', 'bookings']


class TravelBoardRecord(serializers.ModelSerializer):
    board_records = BoardRecordSerializer2Nested(many=True, read_only=True)

    class Meta:
        model = Travel
        fields = ['owner', 'monitor', 'driver', 'bus', 'date', 'time', 'board_records']