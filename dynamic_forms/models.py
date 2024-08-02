from django.db import models, transaction
from django.utils.text import slugify

from base.models import BaseModel, Countable
from django.utils.translation import gettext as _

from dynamic_forms.choices import FormFieldChoices


class IndexCounter(Countable):
    pass


class Field(BaseModel):
    name = models.CharField(max_length=100, null=False, blank=False)
    field_type = models.CharField(max_length=20, choices=FormFieldChoices)
    label = models.CharField(max_length=100)

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


class FormField(BaseModel):
    field = models.ForeignKey(
        Field, on_delete=models.CASCADE, related_name="form_field"
    )
    required = models.BooleanField(default=False)
    validation = models.JSONField(default=list, blank=True)
    options = models.JSONField(default=list, blank=True)
    style = models.TextField(default="", blank=True)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.field.label

    class Meta:
        ordering = ("-updated_at", "-created_at")
        get_latest_by = ("updated_at",)
        verbose_name_plural = _("Form Fields")
        verbose_name = _("Form Field")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.field.name} {str(self.id)[:6]}")
        return super().save()


class Form(BaseModel):
    name = models.CharField(max_length=100)
    fields = models.ManyToManyField(
        FormField, through="FormFieldsOrder", related_name="form_field_order"
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

    # @property
    # def index(self):
    #     if hasattr(self, "form_field_orders"):
    #         breakpoint()
    #         return self.form_field_orders.filter().index


class FormFieldsOrder(BaseModel):
    form_field = models.ForeignKey(
        FormField, on_delete=models.CASCADE, related_name="form_field_orders"
    )
    form = models.ForeignKey(
        Form, on_delete=models.CASCADE, related_name="form_field_orders"
    )
    index = models.IntegerField(default=0)
    slug = None
    is_archived = None
    metadata = None

    def __str__(self):
        return self.form_field.field.name

    class Meta:
        ordering = ("index",)
        get_latest_by = ("updated_at",)
        verbose_name_plural = _("Form Fields Order")
        verbose_name = _("Form Fields Order")
        unique_together = (
            "form_field",
            "form",
            "index",
        )

    def save(self, *args, **kwargs):
        with transaction.atomic():
            max_index = (
                FormFieldsOrder.objects.filter(
                    form_field=self.form_field, form=self.form
                )
                .values_list("index", flat=True)
                .last()
            )
            self.index = (max_index or 0) + 1
        return super().save()
