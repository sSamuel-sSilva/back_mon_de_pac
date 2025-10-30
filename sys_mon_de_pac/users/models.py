from django.contrib.auth.models import AbstractUser, Group
from django.db import models

class CustomUser(AbstractUser):
    TYPE_USERS = [
        ('Admin', 'Admin'),
        ('Motorista', 'Motorista'),
        ('Monitor', 'Monitor'),
        ('Paciente', 'Paciente'),
    ]

    cpf = models.CharField(max_length=11, unique=True, null=False, blank=False, verbose_name='CPF')
    type = models.CharField(max_length=10, null=True, blank=True, choices=TYPE_USERS, verbose_name='Tipo de Usuário')

    def __str__(self):
        return self.username

    
    class Meta:
        verbose_name = "Usuários"
        verbose_name_plural = "Usuários"
        permissions = [
            ("list_user", "Can list users"),
            ("retrieve_user", "Can retrieve user"),
        ]


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
        return f"{self.city} - {self.state}"


class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name='Usuário')
    address = models.OneToOneField(Address, on_delete=models.DO_NOTHING, verbose_name='Endereço')

    name = models.CharField(max_length=100, verbose_name='Nome Completo')
    telephone = models.CharField(max_length=11, verbose_name='Telefone')
    

    def __str__(self):
        return self.name
    

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"


class Card(models.Model):
    uid = models.CharField(max_length=12, unique=True, verbose_name="Identificador Universal")
    in_use = models.BooleanField(default=False,verbose_name="Em Uso")
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.uid


    class Meta:
        verbose_name = "Cartão"
        verbose_name_plural = "Cartões"


    def set_card_on_patient(self, patient):
        try:
            if self.in_use:
                raise ValueError("Cartão já em uso.")

            self.in_use = True
            self.patient = patient
            self.save()
        
        except Patient.DoesNotExist:
            raise ValueError("Paciente não encontrado")

    
    def release_card(self):
        self.patient = None
        self.in_use = False
        self.save() 