from django.db import models
from django.utils.text import slugify

from base.models import BaseModel
from django.utils.translation import gettext as _

from dynamic_forms.choices import FormFieldChoices


class Field(BaseModel):
    name = models.CharField(max_length=100, null=False, blank=False)
    field_type = models.CharField(max_length=20, choices=FormFieldChoices)
    label = models.CharField(max_length=100)
    nested_form = models.ForeignKey(
        "Form",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="nested_fields",
    )

    def __str__(self):
        return self.label

    class Meta:
        ordering = ("-updated_at", "-created_at")
        get_latest_by = ("updated_at",)
        verbose_name_plural = _("Fields")
        verbose_name = _("Field")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save()


class Form(BaseModel):
    name = models.CharField(max_length=100)
    fields = models.ManyToManyField(
        "Field", through="FieldProperty", related_name="form_field_order"
    )

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

    def get_form_field_property(self):
        if hasattr(self, "form_field_property"):
            return self.form_field_property.all()


class FieldProperty(BaseModel):
    field = models.ForeignKey(
        Field, on_delete=models.CASCADE, related_name="form_field_property"
    )
    form = models.ForeignKey(
        Form, on_delete=models.CASCADE, related_name="form_field_property"
    )
    required = models.BooleanField(default=False)
    validation = models.JSONField(default=list, blank=True, null=False)
    options = models.JSONField(default=list, blank=True, null=False)
    style = models.TextField(default="", blank=True, null=False)
    hidden = models.BooleanField(default=False, null=False)
    index = models.IntegerField(default=0, null=False)

    slug = None
    is_archived = None
    metadata = None

    def __str__(self):
        return self.field.name

    class Meta:
        ordering = ("index",)
        get_latest_by = ("updated_at",)
        verbose_name_plural = _("Field Property")
        verbose_name = _("Fields Properties")
        unique_together = (
            "field",
            "form",
            "index",
        )

    @property
    def name(self):
        return self.field.name

    @property
    def label(self):
        return self.field.label

    @property
    def field_type(self):
        return self.field.field_type
