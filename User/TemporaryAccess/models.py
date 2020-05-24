from uuid import uuid4

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models

from .choices import ACCESS_GROUPS

class TemporaryAccessManager(models.Manager):
    def create_activation_access(self, user):
        if not isinstance(user, get_user_model()):
            raise AttributeError('Access must be assigned to User model.')
        access = self.model(
            user = user,
            group = 'a'
        )
        access.save(using=self._db)
        return access
    
    def create_password_forgotten_access(self, user):
        if not isinstance(user, get_user_model()):
            raise AttributeError('Access must be assigned to User model.')
        access = self.model(
            user = user,
            group = 'pw'
        )
        access.save(using=self._db)
        return access

    def create_login_access(self, user):
        if not isinstance(user, get_user_model()):
            raise AttributeError('Access must be assigned to User model.')
        access = self.model(
            user = user,
            group = 'l'
        )
        access.save(using=self._db)
        return access

class TemporaryAccess(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    key = models.CharField(
        max_length=6,
        editable=False,
        primary_key=True
    )
    group = models.CharField(
        max_length=2,
        choices=ACCESS_GROUPS
    )
    creation_date = models.DateTimeField(
        auto_now_add=True
    )

    objects = TemporaryAccessManager()

    @property
    def full_path(self):
        if self.group == 'pw':
            path = settings.ENV['PASSWORD_FORGOTTEN_PATH']
        elif self.group == 'l':
            path = settings.ENV['EMAIL_ACCESS_PATH']
        else:
            path = settings.ENV['ACCOUNT_ACTIVATION_PATH']
        return "{}{}{}".format(
            settings.ENV['BASE_URL'],
            path,
            self.key
        )
    
    @property
    def is_valid(self):
        if self.group == 'pw':
            period_time = int(settings.ENV['PW_FORGOTTEN_KEY_PERIODS_OF_VALIDITY'])
        elif self.group == 'l':
            period_time = int(settings.ENV['ACCES_KEY_PERIODS_OF_VALIDITY'])
        else:
            period_time = int(settings.ENV['ACTIVATION_KEY_PERIODS_OF_VALIDITY'])
        
        limit_time = self.creation_time + timedelta(minutes=period_time)
        return now() < limit_time
        

    def __str__(self):
        return self.key
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.key = uuid4().hex[:6]
            while TemporaryAccess.objects.filter(key=self.key).exists():
                self.key = uuid4().hex[:6]
        super().save(*args, **kwargs)
