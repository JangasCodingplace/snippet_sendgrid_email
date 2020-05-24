from django.dispatch import receiver

from django.db.models.signals import (
    post_save,
)

from django.contrib.auth import get_user_model
User = get_user_model()

from .models import TemporaryAccess

@receiver(post_save, sender=User)
def create_activation_key(*args,**kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        if not user.is_active:
            TemporaryAccess.objects.create_activation_access(
                user = user
            )
