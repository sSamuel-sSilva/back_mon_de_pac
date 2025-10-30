from django.contrib import admin
from django.urls import path, include, re_path
from .views import BusViewSet, TravelViewSet, TravelBookingViewSet, BoardingRecordViewSet
from rest_framework.routers import DefaultRouter
from .consumers import consumer

router = DefaultRouter()
router.register(r'bus', BusViewSet, basename='bus')
router.register(r'travel', TravelViewSet, basename='travel')
router.register(r'travel_booking', TravelBookingViewSet, basename='travel_booking')
router.register(r'boarding_record', BoardingRecordViewSet, basename='boardign_record')


urlpatterns = [
    path('', include(router.urls)),
]
