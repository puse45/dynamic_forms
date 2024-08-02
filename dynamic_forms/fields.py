from django.db import models
from django.utils.translation import gettext_lazy as _


class SerialNumberField(models.IntegerField):
    description = _("Index number string (up to %(max_length)s)")

    def __init__(self, counter_model=None, *args, **kwargs):
        self.counter_model = counter_model
        super(SerialNumberField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        _value = getattr(model_instance, self.attname)
        if add and any([_value == "", not _value]):
            if not self.counter_model.objects.exists():
                self.counter_model.objects.create(counter=0)
            ind = self.counter_model.objects.first()
            length = self.max_length
            code = ("{:0" + str(length) + "d}").format(ind.next_number)
            setattr(model_instance, self.attname, f"{code}")
            return f"{code}"
        else:
            return super(SerialNumberField, self).pre_save(model_instance, add)
