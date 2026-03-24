from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

VitalMonitorDevice

router = DefaultRouter()
router.register(r'user', CustomUserViewSet, basename='user')
router.register(r'patient', PatientViewSet, basename='patient')
router.register(r'companion', CompanionViewSet, basename='companion')
router.register(r'card', CardViewSet, basename='card'),
router.register(r'vital_device', VitalMonitorDeviceViewSet, basename='vital_device'),


urlpatterns = [
    path("", include(router.urls))
]
