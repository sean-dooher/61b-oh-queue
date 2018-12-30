from django.contrib.auth.models import User
from django.db.models.signals import post_save

from .models import Profile, ProfileType

def create_profile_for_user(sender, instance, created, **kwargs):
    if created and not Profile.objects.filter(user=instance).exists():
        Profile.objects.create(user=instance, profile_type=ProfileType.student.value)

post_save.connect(create_profile_for_user, sender=User)
