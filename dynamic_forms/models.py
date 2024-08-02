from django.db import models
from django.utils.text import slugify

from base.models import BaseModel
from django.utils.translation import gettext as _

from dynamic_forms.choices import FormFieldChoices


class FormField(BaseModel):
    name = models.CharField(max_length=100, null=False, blank=False)
    field_type = models.CharField(max_length=20, choices=FormFieldChoices)
    label = models.CharField(max_length=100)
    required = models.BooleanField(default=False)
    validation = models.JSONField(default=list, blank=True)
    options = models.JSONField(default=list, blank=True)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.label

    class Meta:
        ordering = ("-updated_at", "-created_at")
        get_latest_by = ("updated_at",)
        verbose_name_plural = _("Form Fields")
        verbose_name = _("Form Field")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save()


class Form(BaseModel):
    name = models.CharField(max_length=100)
    fields = models.ManyToManyField(FormField)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-updated_at", "-created_at")
        get_latest_by = ("updated_at",)
        verbose_name_plural = _("Form")
        verbose_name = _("Forms")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save()
