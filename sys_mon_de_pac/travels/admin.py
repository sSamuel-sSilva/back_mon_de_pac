from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ['identifier_code', 'driver', 'monitor']


@admin.register(Travel)
class TravelAdmin(admin.ModelAdmin):
    list_display = ['owner', 'monitor', 'driver', 'bus', 'date', 'time']


@admin.register(TravelBooking)
class TravelBookingAdmin(admin.ModelAdmin):
    list_display = ['travel', 'patient', 'date', 'time', 'confirmed', 'canceled']


@admin.register(BoardingRecord)
class BoardingRecordAdmin(admin.ModelAdmin):
    list_display = ['travel_patient', 'patient', 'card', 'bus']
