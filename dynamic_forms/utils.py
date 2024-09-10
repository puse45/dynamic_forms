import re
import zoneinfo

import requests
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django_countries import countries
from phonenumbers import PhoneNumberFormat, format_number
from django_countries.widgets import CountrySelectWidget
from djmoney.forms.fields import MoneyField
from djmoney.forms.widgets import MoneyWidget
from djmoney.money import Money
from phonenumber_field.formfields import PhoneNumberField
from dynamic_forms.choices import FormFieldChoices
from django.core.validators import MinLengthValidator, MaxLengthValidator
from secrets import compare_digest
from datetime import date, datetime


class ArrayField(forms.Field):
    def __init__(self, base_field, *args, **kwargs):
        self.base_field = base_field  # Base field to apply for each array element (e.g., CharField, IntegerField) # noqa: B950
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        # Ensure the value is always a list
        if not value:
            return []
        if isinstance(value, list):
            return value
        # Split the value if it's a string, assuming comma-separated
        return [v.strip() for v in value.split(",")]

    def validate(self, value):
        # Call parent's validation
        super().validate(value)
        # Ensure each item in the array is valid using the base field
        errors = []
        for item in value:
            try:
                self.base_field.clean(item)
            except ValidationError as e:
                errors.append(str(e))
        if errors:
            raise ValidationError(errors)


class ArrayWidget(forms.Textarea):
    def format_value(self, value):
        if value is None:
            return ""
        if isinstance(value, list):
            return ", ".join(str(v) for v in value)
        return value


class NestedFormField(forms.Field):
    def __init__(self, nested_form_instance, *args, **kwargs):
        self.nested_form_instance = nested_form_instance
        super().__init__(*args, **kwargs)

    def clean(self, value):
        if value is None:
            value = {}
        form_class, form_kwargs = build_dynamic_form(self.nested_form_instance)
        nested_form = form_class(data=value, **form_kwargs)
        # Check for missing fields and values
        missing_fields = []
        for field_name, field in nested_form.fields.items():

            if field.required and field_name not in value:
                missing_fields.append(field_name)

        if missing_fields:
            raise forms.ValidationError(
                [f"{field} : This {field} is required." for field in missing_fields]
            )

        if not nested_form.is_valid():
            nested_errors = [
                f"{field}:{error}" for field, error in nested_form.errors.items()
            ]
            # nested_errors = {field: error.get_json_data() for field, error in nested_form.errors.items()} # noqa
            raise forms.ValidationError(
                nested_errors, code="invalid", params={"field": None}
            )
        return nested_form.cleaned_data


class DynamicForm(forms.Form):
    def __init__(self, *args, **kwargs):
        form_fields = kwargs.pop("form_fields")
        form_instance_id = kwargs.pop("form_instance_id")
        super(DynamicForm, self).__init__(*args, **kwargs)
        for field in form_fields:
            field_property = (
                field.form_field_property.select_related("form")
                .filter(form_id=form_instance_id)
                .first()
            )
            field_validators = self.get_validators(field_property.validation)
            if field.field_type == FormFieldChoices.TEXT:
                self.fields[field.name] = forms.CharField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.EMAIL:
                self.fields[field.name] = forms.EmailField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            elif compare_digest(field.field_type, FormFieldChoices.PASSWORD):
                self.fields[field.name] = forms.CharField(
                    label=field.label,
                    required=field_property.required,
                    widget=forms.PasswordInput,
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.CHECKBOX:
                self.fields[field.name] = forms.BooleanField(
                    label=field.label, required=field_property.required
                )
            elif field.field_type == FormFieldChoices.DROPDOWN:
                self.fields[field.name] = forms.ChoiceField(
                    label=field.label,
                    required=field_property.required,
                    choices=[(option, option) for option in field_property.options],
                )

            elif field.field_type == FormFieldChoices.FILE:
                self.fields[field.name] = forms.FileField(
                    label=field.label, required=field_property.required
                )
            elif field.field_type == FormFieldChoices.NESTED:
                self.fields[field.name] = NestedFormField(
                    nested_form_instance=field.nested_form,
                    label=field.label,
                    required=field_property.required,
                )
            elif field.field_type == FormFieldChoices.ARRAY:
                base_field = forms.CharField()
                self.fields[field.name] = ArrayField(
                    base_field=base_field,
                    label=field.label,
                    required=field_property.required,
                    widget=ArrayWidget,
                    validators=field_validators,  # TODO put validation logic
                )
            elif field.field_type == FormFieldChoices.COUNTRY:
                self.fields[field.name] = forms.ChoiceField(
                    label=field.label,
                    required=field_property.required,
                    choices=countries,
                    widget=CountrySelectWidget,  # Use the Country Select dropdown widget
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.CURRENCY:
                self.fields[field.name] = MoneyField(
                    label=field.label,
                    required=field_property.required,
                    widget=MoneyWidget(
                        amount_widget=forms.TextInput(attrs={"placeholder": "Amount"})
                    ),
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.DATE:
                self.fields[field.name] = forms.DateField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                    widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
                )
            if field.field_type == FormFieldChoices.DATE_RANGE:
                self.fields[field.name] = forms.DateField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                    widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
                )

            elif field.field_type == FormFieldChoices.DATE_TIME:
                self.fields[field.name] = forms.DateTimeField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                    widget=forms.DateTimeInput(
                        format="%Y-%m-%d %H:%M:%S", attrs={"type": "datetime-local"}
                    ),
                )

            elif field.field_type == FormFieldChoices.DATE_TIME_RANGE:
                self.fields[field.name] = forms.DateTimeField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                    widget=forms.DateTimeInput(
                        format="%Y-%m-%d %H:%M:%S", attrs={"type": "datetime-local"}
                    ),
                )

            elif field.field_type == FormFieldChoices.KRA_PIN:
                self.fields[field.name] = forms.CharField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.NATIONAL_ID:
                self.fields[field.name] = forms.CharField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            if field.field_type == FormFieldChoices.FLOAT:
                self.fields[field.name] = forms.FloatField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            if field.field_type == FormFieldChoices.NUMBER:
                self.fields[field.name] = forms.IntegerField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            if field.field_type == FormFieldChoices.UUID:
                self.fields[field.name] = forms.UUIDField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            if field.field_type == FormFieldChoices.RADIO:
                self.fields[field.name] = forms.ChoiceField(
                    label=field.label,
                    required=field_property.required,
                    choices=[(option, option) for option in field_property.options],
                )

            if field.field_type == FormFieldChoices.URL:
                self.fields[field.name] = forms.URLField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.PHONE_NUMBER:
                self.fields[field.name] = PhoneNumberField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )

    def get_validators(self, validations):
        validators = []
        _max_length = "max_length"
        _min_length = "min_length"
        max_length_pattern = rf"{_max_length}:\d+"
        min_length_pattern = rf"{_min_length}:\d+"
        for validation in validations:
            if validation.startswith("min_length"):
                min_length = int(validation.split(":")[1])
                validators.append(MinLengthValidator(min_length))
            if validation.startswith("max_length"):
                max_length = int(validation.split(":")[1])
                validators.append(MaxLengthValidator(max_length))
            if validation.startswith("date_range"):
                start_date, end_date = validation.split(":")[1].split(",")
                validators.append(self.date_range_validator(start_date, end_date))
            if validation.startswith("datetime_range"):
                start_datetime, end_datetime = validation.split("datetime_range:")[
                    1
                ].split(",")
                validators.append(
                    self.datetime_range_validator(start_datetime, end_datetime)
                )
            if validation.startswith("revenue_pin_validation_base_url"):
                kra_base_url = validation.split("revenue_pin_validation_base_url:")[1]
                validators.append(self.internal_resource_validator(kra_base_url))
            if validation.startswith("id_validation_base_url"):
                iprs_base_url = validation.split("id_validation_base_url:")[1]
                validators.append(self.internal_resource_validator(iprs_base_url))
            min_length_pattern_checker = self.check_regex(
                min_length_pattern, validation
            )
            max_length_pattern_checker = self.check_regex(
                max_length_pattern, validation
            )
            if min_length_pattern_checker:
                min_length_ = int(validation.split(f"{_min_length}:")[1])
                validators.append(MinLengthValidator(min_length_))
            if max_length_pattern_checker:
                max_length_ = int(validation.split(f"{_max_length}:")[1])
                validators.append(MaxLengthValidator(max_length_))
        return validators

    def date_range_validator(self, start_date_str, end_date_str):
        def validator(value):
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
            if not (start_date <= value <= end_date):
                raise ValidationError(
                    f"Date must be between {start_date_str} and {end_date_str}."
                )

        return validator

    def datetime_range_validator(self, start_datetime_str, end_datetime_str):
        def validator(value):
            start_datetime = datetime.fromisoformat(start_datetime_str).replace(
                tzinfo=zoneinfo.ZoneInfo(key="UTC")
            )
            end_datetime = datetime.fromisoformat(end_datetime_str).replace(
                tzinfo=zoneinfo.ZoneInfo(key="UTC")
            )
            if not (start_datetime <= value <= end_datetime):
                raise ValidationError(
                    f"DateTime must be between {start_datetime_str} and {end_datetime_str}."
                )

        return validator

    def internal_resource_validator(self, base_url):
        def validator(value):
            if not base_url:
                raise ValidationError(
                    "KRA PIN validation service URL is not configured."
                )
            # Make the request to the validation service
            try:
                if settings.DEBUG:  # Temp Fix to test
                    return True
                response = requests.get(f"{base_url}/{value}")
                if response.status_code != 200:
                    raise ValidationError(f"Invalid KRA PIN: {value}")
            except requests.exceptions.RequestException as e:
                raise ValidationError(
                    f"Error contacting KRA PIN validation service: {e}"
                )

        return validator

    def clean(self):
        cleaned_data = super().clean()
        for field_name, field_value in cleaned_data.items():
            field = self.fields.get(field_name)
            if isinstance(field, MoneyField):
                if isinstance(cleaned_data[field_name], Money):
                    cleaned_data[field_name] = {
                        "amount": str(cleaned_data[field_name].amount),
                        "currency": cleaned_data[field_name].currency.code,
                    }
            if isinstance(field, PhoneNumberField):
                # Ensure the value is a string before trying to convert it to a phone number
                if isinstance(field_value, int):
                    field_value = str(field_value)
                    cleaned_data[field_name] = field_value  # Update the cleaned data
                cleaned_data[field_name] = format_number(
                    field_value, PhoneNumberFormat.INTERNATIONAL
                )

        return cleaned_data

    @staticmethod
    def check_regex(pattern, validation):
        if re.search(pattern, validation):
            return True
        return False


def build_dynamic_form(form_instance):
    return DynamicForm, {
        "form_fields": form_instance.fields.all(),
        "form_instance_id": form_instance.id,
    }
