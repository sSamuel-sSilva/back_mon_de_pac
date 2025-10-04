from django.db import models
from django.core.exceptions import ValidationError
from users.models import Card

class Bus(models.Model):
    driver = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name='Motorista', related_name="bus_driver")
    monitor = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name='Monitor', related_name="bus_monitor")


    def __str__(self):
        return self.id
    

    def clean(self):
        super.clean()
        if self.driver.type != 'Motorista':
            raise ValidationError({'Motorista': 'O usuário selecionado não é um motorista.'})
        if self.monitor.type != 'Monitor':
            raise ValidationError({'Monitor': 'O usuário selecionado não é um monitor.'})


    def save(self, force_insert = ..., force_update = ..., using = ..., update_fields = ...):
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)
    

class Travel(models.Model):
    owner = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name='Criador', related_name="travel_owner")
    monitor = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name='Monitor', related_name="travel_monitor")
    driver = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name='Motorista', related_name="travel_driver")

    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, verbose_name='Ônibus')

    date = models.DateField(verbose_name='Data da Viagem')
    time = models.TimeField(verbose_name='Hora da Viagem')


    def __str__(self):
        return f"{self.date} - {self.time} | Criado por: {self.admin}" 


    def clean(self):
        super.clean()
        if self.driver.type != 'Motorista':
            raise ValidationError({'Motorista': 'O usuário selecionado não é um motorista.'})
        if self.monitor.type != 'Monitor':
            raise ValidationError({'Monitor': 'O usuário selecionado não é um monitor.'})
        if self.admin.type != 'Admin':
            raise ValidationError({'Administrador': 'O usuário selecionado não é um administrador.'})


    def save(self, force_insert = ..., force_update = ..., using = ..., update_fields = ...):
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)
    

    class Meta:
        verbose_name = "Viagem"
        verbose_name_plural = "Viagens"


class TravelBooking(models.Model):
    travel = models.ForeignKey(Travel, on_delete=models.CASCADE, verbose_name='Viagem')
    patient = models.ForeignKey('users.Patient', on_delete=models.CASCADE, verbose_name='Paciente')

    date = models.DateField(verbose_name='Data do Agendamento', auto_now_add=True)
    time = models.TimeField(verbose_name='Hora do Agendamento', auto_now_add=True)

    confirmed = models.BooleanField(default=False, verbose_name='Confirmação do Agendamento')
    canceled = models.BooleanField(default=False, verbose_name='Cancelamento do Agendamento')


    def __str__(self):
        return f"Viagem: {self.travel} | Paciente: {self.patient}"


    class Meta:
        verbose_name = "Agendamento de Viagem do Paciente"
        verbose_name_plural = "Agendamentos de Viagens dos Pacientes"


class BoardingRecord(models.Model):
    travel_patient = models.OneToOneField(TravelBooking, on_delete=models.CASCADE, verbose_name='Agendamento de Viagem do Paciente')
    card = models.OneToOneField(Card, on_delete=models.CASCADE, verbose_name='Cartão')
    bus = models.OneToOneField(Bus, on_delete=models.DO_NOTHING)

    # pensando se isso vale a pena, pq se eu for modificar o "on_board" eu perco a data e hora originais
    date = models.DateField(verbose_name='Data da Associação', auto_now_add=True)
    time = models.TimeField(verbose_name='Hora da Associação', auto_now_add=True)
    on_board = models.BooleanField(default=False, verbose_name='Embarcado')


    def __str__(self):
        return f"Agendamento: {self.travel_patient} | Cartão: {self.card}"


    class Meta:
        verbose_name = "Associação de Cartão ao Agendamento"
        verbose_name_plural = "Associações de Cartões aos Agendamentos"