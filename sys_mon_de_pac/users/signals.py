from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def add_user_to_group(sender, instance, created, **kwargs):
    if instance.type:
        group = Group.objects.get(name=instance.type)
        instance.groups.clear()
        instance.groups.add(group)

        if instance.type == 'Admin':
            instance.is_istaff = True
        

