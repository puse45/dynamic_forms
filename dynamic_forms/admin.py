from django.contrib import admin

from dynamic_forms.models import FormField, Form


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = [
        "label",
        "name",
        "slug",
        "field_type",
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
        "label",
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
    filter_horizontal = ("fields",)
