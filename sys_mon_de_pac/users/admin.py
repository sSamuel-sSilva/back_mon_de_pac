from django.contrib import admin
from .models import *
from .forms import PatientForm

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'type')
    list_filter = ('type', )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass


class CustomUserInline(admin.StackedInline):
    model = CustomUser
    extra = 1


class AddressInline(admin.StackedInline):
    model = Address
    extra = 1


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    form = PatientForm

    list_display = ('name', 'get_cpf', 'telephone')

    def get_cpf(self, obj):
        return obj.user.cpf

    get_cpf.short_description = "CPF"


@admin.register(Companion)
class CompanionAdmin(admin.ModelAdmin):
    pass


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('uid', 'in_use', 'get_patient')
    search_fields = ('uid',)

    def get_patient(self, obj):
        patient = obj.patient
        if patient:
            return patient
        
        return "None"

    get_patient.short_description = "Paciente Atual"