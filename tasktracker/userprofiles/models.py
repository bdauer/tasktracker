from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    most_recent_login = models.DateField(default=timezone.now)

# Create your models here.

    @receiver(user_logged_out, sender=User)
    def save_last_login(sender, request, user, **kwargs):
        profile = user.profile
        profile.most_recent_login = user.last_login
        profile.save()
