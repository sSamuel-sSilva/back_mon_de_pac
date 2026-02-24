from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ValidationError
from django.db import models

class CustomUser(AbstractUser):
    # TYPE_USERS = [
    #     ('Admin', 'Admin'),
    #     ('Motorista', 'Motorista'),
    #     ('Monitor', 'Monitor'),
    #     ('Paciente', 'Paciente'),
    # ]

    class UserType(models.IntegerChoices):
        ADMIN = 0, "Admin"
        MOTORISTA = 1, "Motorista"
        MONITOR = 2, "Monitor"
        PACIENTE = 3, "Paciente"


    cpf = models.CharField(max_length=11, unique=True, null=True, blank=True, verbose_name='CPF')
    type = models.IntegerField(default=UserType.PACIENTE, choices=UserType.choices, verbose_name='Tipo de Usuário')


    def save(self, *args, **kwargs):
        if self.type == 'Admin' or self.type == 'Monitor':
            self.is_staff = True
            self.is_superuser = True

        if self.is_staff or self.is_superuser:
            self.type = 0 

        self.full_clean()
        super().save(*args, **kwargs)


    def clean(self):
        super().clean()

        if (self.type != 'Admin') and (self.type != 'Monitor') and (not self.is_superuser) and not self.cpf:
            raise ValidationError({
                'cpf': 'CPF é obrigatório para este tipo de usuário.'
            })


    def __str__(self):
        return self.username

    
    class Meta:
        verbose_name = "Usuários"
        verbose_name_plural = "Usuários"


class Address(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name='Usuário')
    
    cep = models.CharField(max_length=10, verbose_name="CEP", blank=True)
    street = models.CharField(max_length=100, verbose_name='Rua')
    number = models.CharField(max_length=10, verbose_name='Número')
    city = models.CharField(max_length=50, verbose_name='Cidade')
    state = models.CharField(max_length=50, verbose_name='Estado')
    complement = models.CharField(max_length=128, verbose_name="Complemento")
    neighborhood = models.CharField(max_length=128, verbose_name="Bairro")


    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"


    def __str__(self):
        return f"{self.street}, {self.number}"


class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name='Usuário')
    address = models.OneToOneField(Address, on_delete=models.DO_NOTHING, verbose_name='Endereço')

    name = models.CharField(max_length=255, verbose_name='Nome Completo')
    telephone = models.CharField(max_length=11, verbose_name='Telefone')
    

    def __str__(self):
        return self.name
    

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"


class Companion(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nome Completo")
    telephone = models.CharField(max_length=11, verbose_name="Telefone")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Acompanhante"
        verbose_name_plural = "Acompanhantes"


class Card(models.Model):
    uid = models.CharField(max_length=12, unique=True, verbose_name="Identificador Universal")
    in_use = models.BooleanField(default=False,verbose_name="Em Uso")
    # patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.uid


    class Meta:
        verbose_name = "Cartão"
        verbose_name_plural = "Cartões"


    # def set_card_on_patient(self, patient):
    def set_use_as_true(self, patient):
        # try:
        if self.in_use:
            raise ValueError("Cartão já em uso.")

        self.in_use = True
        # self.patient = patient
        self.save()
        
        # except Patient.DoesNotExist:
        #     raise ValueError("Paciente não encontrado")

    
    def release_card(self):
        self.in_use = False
        self.save() 
        # self.patient = None