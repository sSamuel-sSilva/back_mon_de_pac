from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

# Register your models here.


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('cpf', 'type')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('cpf', 'type')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass


# class CustomUserInline(admin.StackedInline):
#     model = CustomUser
#     extra = 1


# class AddressInline(admin.StackedInline):
#     model = Address
#     extra = 1


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_cpf', 'telephone')

    def get_cpf(self, obj):
        return obj.user.cpf

    get_cpf.short_description = "CPF"


@admin.register(Companion)
class CompanionAdmin(admin.ModelAdmin):
    pass


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('uid', 'in_use')
    search_fields = ('uid',)


@admin.register(VitalMonitorDevice)
class VitalMonitorDeviceAdmin(admin.ModelAdmin):
    list_display = ('code', 'in_use')
    search_fields = ('uid',)