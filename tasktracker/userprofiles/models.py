from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_out

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    most_recent_login = models.DateField()

# Create your models here.

    @receiver(user_logged_out, sender)
    def save_last_login(sender, request, user):
        self.most_recent_login = user.last_login
        self.save()
