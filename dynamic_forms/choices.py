from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class FormFieldChoices(TextChoices):
    TEXT = "text", _("Text")
    EMAIL = "email", _("Email")
    PASSWORD = "password", _("Password")
    CHECKBOX = "checkbox", _("Check Box")
    DROPDOWN = "dropdown", _("Drop Down")
