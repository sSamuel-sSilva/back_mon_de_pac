from django.contrib import admin
from django.urls import path, include
from .views import UserViewSet, PatientViewSet, CardViewSet 
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'patient', PatientViewSet, basename='patient')
router.register(r'card', CardViewSet, basename='card')


urlpatterns = [
    path('', include(router.urls))
]
