from django.contrib import admin

from dynamic_forms.forms import FieldPropertyForm
from dynamic_forms.models import Form, Field, FieldProperty


class InlineFormFieldsOrder(admin.TabularInline):
    model = FieldProperty
    fields = (
        "index",
        "field",
        "required",
        "hidden",
        "validation",
        "options",
        "style",
    )
    extra = 1
    form = FieldPropertyForm


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


@admin.register(FieldProperty)
class FormFieldsOrderAdmin(admin.ModelAdmin):
    list_display = [
        "index",
        "field",
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
