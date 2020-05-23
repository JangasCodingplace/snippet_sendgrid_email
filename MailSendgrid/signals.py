from django.template.loader import get_template
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.utils.timezone import now

from django.db.models.signals import (
    post_save,
    pre_save
)
from django.contrib.auth.signals import user_logged_in

User = get_user_model()

@receiver(post_save, sender=User)
def send_mail_to_user(*args, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        """
        Send Registration / Activation Mail
        """
        registration_info_mail_body = get_template('registration.html')
        context = {
            'user':user
        }

        mail = registration_info_mail_body.render(context)
        # print(mail)

@receiver(pre_save, sender=User)
def send_chainge_mail_to_user(*args,**kwargs):
    user = kwargs['instance'] 
    try:
        prev_user = User.objects.get(pk=user.pk)
    except User.DoesNotExist:
        return
    
    if user.email != prev_user.email:
        """
        Send Emailchange Mail
        """
        email_change_info_mail_body = get_template('email_chainged.html')
        context = {
            'user':user,
            'prev_user':prev_user
        }
        mail = email_change_info_mail_body.render(context)
        # print(mail)

@receiver(user_logged_in)
def send_login_mail(*args,**kwargs):
    user = kwargs['user']
    if user.last_login is not None:
        """
        Send Logininfo Mail
        """
        login_info_mail_body = get_template('login_info.html')
        context = {
            'user':user,
            'date':now()
        }
        mail = login_info_mail_body.render(context)
        # print(mail)
