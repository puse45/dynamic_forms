import re

from django import forms
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from dynamic_forms.choices import FormFieldChoices
from dynamic_forms.models import FieldProperty, Field

validation_pattern = r"(\w+:\w+|\w+)"  # "min_length:8" # noqa: B950
date_range_validation_pattern = r"^date_range:(\d{4}-\d{2}-\d{2}),(\d{4}-\d{2}-\d{2})$"  # "date_range:1980-01-01,2025-12-31" # noqa: B950
date_time_range_validation_pattern = r"^datetime_range:(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}),(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})$"  # datetime_range:2024-01-01T08:00:00,2025-12-31T18:00:00, datetime_range:2024-01-01 08:00:00,2025-12-31 18:00:00 # noqa: B950
revenue_pin_validation_base_url_pattern = r"^revenue_pin_validation_base_url:http[s]?://[a-zA-Z0-9.-]+(/[a-zA-Z0-9.-]+)*$"  # "kra_base_url:https://api.example.com/validate-kra-pin" # noqa: B950
id_validation_base_url_pattern = r"^id_validation_base_url:http[s]?://[a-zA-Z0-9.-]+(/[a-zA-Z0-9.-]+)*$"  # "id_validation_base_url:https://api.example.com/validate-kra-pin" # noqa: B950


class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        exclude = ["created_at", "updated_at"]

    def clean(self):
        name = self.cleaned_data.get("name")
        field_type = self.cleaned_data.get("field_type")
        nested_form = self.cleaned_data.get("nested_form")

        if field_type == FormFieldChoices.NESTED and not nested_form:
            raise forms.ValidationError({"nested_form": _("This field is required")})
        if name:
            self.cleaned_data["name"] = slugify(name.lower())

        return self.cleaned_data


class FieldPropertyForm(forms.ModelForm):
    class Meta:
        model = FieldProperty
        exclude = ["created_at", "updated_at"]

    def clean(self):
        field = self.cleaned_data.get("field")
        required = self.cleaned_data.get("required")
        validation = self.cleaned_data.get("validation")
        options = self.cleaned_data.get("options")
        hidden = self.cleaned_data.get("hidden")

        if (
            field.field_type in [FormFieldChoices.DROPDOWN, FormFieldChoices.RADIO]
            and not options
        ):
            raise forms.ValidationError({"options": _("Options are required.")})
        if field.field_type == FormFieldChoices.DATE_RANGE and validation:
            for _s in validation:
                match = re.fullmatch(date_range_validation_pattern, str(validation[0]))
                if not match:
                    raise forms.ValidationError(
                        {
                            "validation": _(
                                'Not a valid validation format ie. ["date_range:1980-01-01,2025-12-31"].'  # noqa
                            )
                        }
                    )
        if field.field_type == FormFieldChoices.DATE_TIME_RANGE and validation:
            if validation:
                match = re.fullmatch(
                    date_time_range_validation_pattern, str(validation[0])
                )
                if not match:
                    raise forms.ValidationError(
                        {
                            "validation": _(
                                'Not a valid validation format ie. ["datetime_range:2024-01-01T08:00,2025-12-31T18:00"].'  # noqa
                            )
                        }
                    )

        if field.field_type == FormFieldChoices.KRA_PIN:
            if not validation:
                raise forms.ValidationError(
                    {"validation": _("validation are required.")}
                )
            if validation:
                match = re.fullmatch(
                    revenue_pin_validation_base_url_pattern, str(validation[0])
                )
                if not match:
                    raise forms.ValidationError(
                        {
                            "validation": _(
                                'Not a valid validation format ie. ["revenue_pin_validation_base_url:https://api.example.com/"].'  # noqa
                            )
                        }
                    )

        if field.field_type == FormFieldChoices.NATIONAL_ID:
            if not validation:
                raise forms.ValidationError(
                    {"validation": _("validation are required.")}
                )
            if validation:
                match = re.fullmatch(id_validation_base_url_pattern, str(validation[0]))
                if not match:
                    raise forms.ValidationError(
                        {
                            "validation": _(
                                'Not a valid validation format ie. ["id_validation_base_url:https://api.example.com"].'  # noqa
                            )
                        }
                    )

        if required and hidden:
            raise forms.ValidationError(
                {"required": _("Required cannot be True if Hidden is True.")}
            )
        # TODO use contains to check of multiple validators
        if validation and field.field_type not in [
            FormFieldChoices.DATE_RANGE,
            FormFieldChoices.DATE_TIME_RANGE,
            FormFieldChoices.KRA_PIN,
            FormFieldChoices.NATIONAL_ID,
        ]:
            for _s in validation:
                match = re.fullmatch(validation_pattern, _s)
                if not match:
                    raise forms.ValidationError(
                        {
                            "validation": _(
                                'Not a valid validation format ie. ["min_length:5","max_length:10"].'  # noqa
                            )
                        }
                    )

        return self.cleaned_data
