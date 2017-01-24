from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    most_recent_login = models.DateField(default=timezone.now)

@receiver(user_logged_out, sender=User)
def save_last_login(sender, request, user, **kwargs):
    profile = user.profile
    profile.most_recent_login = user.last_login
    profile.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
