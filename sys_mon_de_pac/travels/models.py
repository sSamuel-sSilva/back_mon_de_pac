# from django.db import models, transaction
# from django.db.models import F
# from django.core.exceptions import ValidationError
# from users.models import Card, Patient, Companion, CustomUser

# # Importações dos Signals
# from django.db.models.signals import pre_delete
# from django.dispatch import receiver

# class Bus(models.Model):
#     identifier_code = models.CharField(max_length=100, verbose_name='Identificador', unique=True)

#     def __str__(self):
#         return self.identifier_code
    
#     class Meta:
#         verbose_name = "Ônibus"
#         verbose_name_plural = "Caravana"


# class Destiny(models.Model):
#     destiny = models.CharField(max_length=64)

#     def __str__(self):
#         return self.destiny

#     class Meta:
#         verbose_name = "Destino"
#         verbose_name_plural = "Destinos"


# class Travel(models.Model):

#     class Status(models.IntegerChoices):
#         PENDENTE = 0, "Pendente"
#         ANDAMENTO = 1, "Andamento"
#         CONCLUIDA = 2, "Concluída"
    
#     owner = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name='Criador', related_name="travel_owner")
#     monitor = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name='Monitor', related_name="travel_monitor")
#     driver = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name='Motorista', related_name="travel_driver")

#     destiny = models.ForeignKey(Destiny, on_delete=models.DO_NOTHING, verbose_name='Destino')
#     bus = models.ForeignKey(Bus, on_delete=models.CASCADE, verbose_name='Ônibus')
#     vacations = models.IntegerField(default=31, verbose_name="Vagas para viagem", blank=False, null=False)

#     date = models.DateField(verbose_name='Data da Viagem')
#     time = models.TimeField(verbose_name='Hora da Viagem')

#     status = models.IntegerField(default=Status.PENDENTE, choices=Status.choices, verbose_name="Status da Viagem")


#     def __str__(self):
#         date = self.date.strftime("%d/%m/%Y")
#         return f"Viagem para {self.destiny} - {date} - {self.time}" 


#     def clean(self):
#         super(Travel, self).clean()
#         if self.driver and self.driver.type != CustomUser.UserType.MOTORISTA:
#             raise ValidationError({'Motorista': 'O usuário selecionado não é um motorista.'})
#         if self.monitor and self.monitor.type != CustomUser.UserType.MONITOR:
#             raise ValidationError({'Monitor': 'O usuário selecionado não é um monitor.'})
#         if self.owner and self.owner.type != CustomUser.UserType.ADMIN:
#             raise ValidationError({'Administrador': 'O usuário selecionado não é um administrador.'})


#     def save(self, *args, **kwargs):
#         self.full_clean()
#         super().save(*args, **kwargs)
    

#     class Meta:
#         verbose_name = "Viagem"
#         verbose_name_plural = "Viagens"


# class TravelBooking(models.Model):
#     class Status(models.IntegerChoices):
#         PENDENTE = 0, "Pendente"
#         CANCELADO = 1, "Cancelado"
#         CONFIRMADO = 2, "Confirmado"

#     travel = models.ForeignKey(Travel, on_delete=models.CASCADE, verbose_name='Viagem')
#     patient = models.ForeignKey('users.Patient', on_delete=models.CASCADE, verbose_name='Paciente')
#     companion = models.ForeignKey('users.Companion', on_delete=models.DO_NOTHING, verbose_name='Acompanhante', null=True, blank=True)

#     card = models.ForeignKey('users.Card', on_delete=models.DO_NOTHING, verbose_name='Cartão do usuário', null=True, blank=True)
#     need_vital_monitor_device = models.BooleanField(default=False, verbose_name="Paciente precisa de monitoramento?")
#     vital_monitor_device = models.ForeignKey('users.VitalMonitorDevice', on_delete=models.DO_NOTHING, verbose_name='Dispositivo de Monitoramento do usuário', null=True, blank=True)

#     date = models.DateField(verbose_name='Data do Agendamento', auto_now_add=True)
#     time = models.TimeField(verbose_name='Hora do Agendamento', auto_now_add=True)

#     status = models.IntegerField(default=Status.PENDENTE, choices=Status.choices, verbose_name="Status da Solicitação")


#     def __str__(self):
#         return f"Viagem: {self.travel} | Paciente: {self.patient}"


#     class Meta:
#         verbose_name = "Solicitação"
#         verbose_name_plural = "Solicitações"



# class BoardingRecord(models.Model):
#     travel_booking = models.OneToOneField(TravelBooking, on_delete=models.CASCADE, verbose_name='Solicitação de Viagem')
#     patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, verbose_name='Paciente')
#     card = models.ForeignKey(Card, on_delete=models.DO_NOTHING, verbose_name='Cartão')
#     bus = models.ForeignKey(Bus, on_delete=models.DO_NOTHING)

#     on_board = models.BooleanField(default=False, verbose_name='Embarcado')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Agendamento: {self.travel_booking} | Cartão: {self.card}"


#     class Meta:
#         verbose_name = "Registro de Embarque"
#         verbose_name_plural = "Registros de Embarque"


# # =========================================================================
# # GATILHOS (SIGNALS) DE SEGURANÇA ABSOLUTA
# # =========================================================================

# @receiver(pre_delete, sender=TravelBooking)
# def release_resources_on_booking_delete(sender, instance, **kwargs):
#     """
#     Sempre que um TravelBooking (solicitação) for deletado do banco
#     (seja por exclusão direta, seja porque o Paciente dono dela foi deletado).
#     Usamos o comando .update() para forçar a gravação direto no banco de dados
#     e evitar que a cascata do Django ignore a liberação.
#     """
#     from users.models import Card, VitalMonitorDevice
    
#     # 1. Libera o cartão RFID (se existir) direto no Banco de Dados
#     if getattr(instance, 'card_id', None):
#         Card.objects.filter(pk=instance.card_id).update(in_use=False)
        
#     # 2. Libera o dispositivo vital (se existir) direto no Banco de Dados
#     if getattr(instance, 'need_vital_monitor_device', False) and getattr(instance, 'vital_monitor_device_id', None):
#         VitalMonitorDevice.objects.filter(pk=instance.vital_monitor_device_id).update(in_use=False)
        
#     # 3. Devolve a vaga para a viagem (se a pessoa estava confirmada) direto no Banco de Dados
#     if instance.status == 2 and getattr(instance, 'travel_id', None):
#         vac = 2 if instance.companion_id else 1
#         Travel.objects.filter(pk=instance.travel_id).update(vacations=F('vacations') + vac)
