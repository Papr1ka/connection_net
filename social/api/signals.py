from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .models import UserModel


@receiver(post_save, sender=User)
def create_profile(instance, created, **kwargs):
    if created:
        print(instance)
        UserModel.objects.create(user=instance)

@receiver(pre_save, sender=UserModel)
def delete_old_image(instance, **kwargs):
    print(instance.avatar_image.name)
    print(instance, kwargs)

@receiver(post_save, sender=UserModel)
def delete_old_image(instance, created, **kwargs):
    print(instance.avatar_image.name)
    print(instance, kwargs)
    print(created)