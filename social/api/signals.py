from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import UserModel


@receiver(post_save, sender=User)
def create_profile(instance, created, **kwargs):
    if created:
        print(instance)
        UserModel.objects.create(user=instance)
