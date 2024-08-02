from django.contrib import admin

from dynamic_forms.forms import FormFieldForm
from dynamic_forms.models import FormField, Form, Field, FormFieldsOrder


class InlineFormFieldsOrder(admin.TabularInline):
    model = FormFieldsOrder
    fields = ("index", "form_field")
    extra = 1


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "label",
        "field_type",
        "slug",
        "is_archived",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "is_archived",
        "created_at",
        "updated_at",
    ]
    list_display_links = [
        "name",
    ]
    search_fields = ["name", "label", "id"]
    readonly_fields = ["slug", "metadata"]
    list_per_page = 50
    save_on_top = True


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = [
        "field",
        "slug",
        "required",
        "is_archived",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "required",
        "is_archived",
        "created_at",
        "updated_at",
    ]
    list_display_links = [
        "field",
    ]
    search_fields = ["field__name", "field__label", "id"]
    readonly_fields = ["slug", "metadata"]
    list_per_page = 50
    save_on_top = True
    form = FormFieldForm


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "is_archived",
        "created_at",
        "updated_at",
    ]
    search_fields = ["name", "id"]
    readonly_fields = ["slug", "metadata"]
    list_per_page = 50
    save_on_top = True
    inlines = [InlineFormFieldsOrder]


@admin.register(FormFieldsOrder)
class FormFieldsOrderAdmin(admin.ModelAdmin):
    list_display = [
        "index",
        "form_field",
        "form",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "id",
    ]
    list_per_page = 50
    save_on_top = True
