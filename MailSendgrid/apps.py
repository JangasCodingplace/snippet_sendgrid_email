from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MailSendgridConfig(AppConfig):
    name = 'MailSendgrid'
    verbose_name = _("Sendgrid")

    def ready(self):
        import MailSendgrid.signals
