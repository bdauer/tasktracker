from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Profile(models.Model):
    """
    For now, profile is being used to track most_recent_login.
    Eventually it may be used to generate a profile page
    and store user-specific settings.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    most_recent_login = models.DateField(default=timezone.now)

@receiver(user_logged_out, sender=User)
def save_last_login(sender, request, user, **kwargs):
    """
    Updates last_login with most_recent_login
    when a user logs out.

    The recency of last login is used to determine
    whether or not to update daily recurring tasks
    for a user. If the user hasn't logged in recently,
    then their recurring tasks don't create new instances.

    If/when that user logs back in, all of the updates
    that never occurred are processed.
    """
    profile = user.profile
    profile.most_recent_login = user.last_login
    profile.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    When a new user is created, creates a profile for them.
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    When a new user is created, saves their profile.
    """
    instance.profile.save()
