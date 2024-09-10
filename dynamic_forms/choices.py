from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class FormFieldChoices(TextChoices):
    ARRAY = "array", _("Array")
    CHECKBOX = "checkbox", _("Check Box")
    COUNTRY = "country", _("Country")
    COUNTY = "county", _("County")
    CURRENCY = "currency", _("Currency")
    DATE = "date", _("Date")
    DATE_RANGE = "date_range", _("Date Range")
    DATE_TIME = "date_time", _("Date Time")
    DATE_TIME_RANGE = "date_time_range", _("Date Time Range")
    DROPDOWN = "dropdown", _("Drop Down")
    EMAIL = "email", _("Email")
    FILE = "file", _("File")
    FLOAT = "float", _("Float")
    KRA_PIN = "kra_pin", _("KRA PIN")
    NATIONAL_ID = "national_id", _("National ID")
    NESTED = "nested", _("Nested Form")
    NUMBER = "number", _("Number")
    PASSWORD = "password", _("Password")
    PHONE_NUMBER = "phone_number", _("Phone Number")
    RADIO = "radio", _("Radio")
    TEXT = "text", _("Text")
    URL = "url", _("URL")
    UUID = "uuid", _("UUID")
