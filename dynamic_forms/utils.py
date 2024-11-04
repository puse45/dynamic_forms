import re
import zoneinfo
from secrets import compare_digest
from datetime import date, datetime, time
import requests
from djmoney.contrib.django_rest_framework import MoneyField
from djmoney.money import Money
from phonenumbers.phonenumberutil import format_number, PhoneNumberFormat
from rest_framework import serializers
from django_countries.serializer_fields import CountryField
from phonenumber_field.serializerfields import PhoneNumberField
from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from .models import FormFieldChoices


class NestedFormSerializer(serializers.ListSerializer):

    def __init__(self, nested_form_instance, field, *args, **kwargs):
        self.nested_form_instance = nested_form_instance
        self.field = field
        child_serializer_class, serializer_kwargs = build_dynamic_serializer(
            self.nested_form_instance
        )
        serializer_fields = serializer_kwargs.pop("form_fields")
        form_instance = serializer_kwargs.pop("form_instance")
        kwargs["child"] = child_serializer_class(
            data={}, form_fields=serializer_fields, form_instance=form_instance
        )
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if data is None:
            data = []
        if not isinstance(data, list):
            data = [data]

        errors = []
        cleaned_data_list = []
        serializer_class, serializer_kwargs = build_dynamic_serializer(
            self.nested_form_instance
        )
        serializer_fields = serializer_kwargs.pop("form_fields")
        form_instance = serializer_kwargs.pop("form_instance")
        if not data:
            nested_form = serializer_class(
                data={}, form_fields=serializer_fields, form_instance=form_instance
            )
            if not nested_form.is_valid():
                errors.append({self.field.name: [nested_form.errors]})
        for value in data:
            nested_serializer = serializer_class(
                data=value, form_fields=serializer_fields, form_instance=form_instance
            )
            missing_fields = []
            for field_name, field in nested_serializer.fields.items():
                if field.required and field_name not in value:
                    missing_fields.append(field_name)

            if not nested_serializer.is_valid():
                errors.append(nested_serializer.errors)
            else:
                cleaned_data_list.append(nested_serializer.validated_data)

        if errors:
            raise serializers.ValidationError(errors)
        return cleaned_data_list


class DynamicSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        form_fields = kwargs.pop("form_fields")
        form_instance = kwargs.pop("form_instance")
        super(DynamicSerializer, self).__init__(*args, **kwargs)

        for field in form_fields:
            field_property = (
                field.form_field_property.select_related("form")
                .filter(form=form_instance)
                .first()
            )
            field_validators = self.get_validators(field_property.validation)

            if field.field_type == FormFieldChoices.TEXT:
                self.fields[field.name] = serializers.CharField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.EMAIL:
                self.fields[field.name] = serializers.EmailField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            elif compare_digest(field.field_type, FormFieldChoices.PASSWORD):
                self.fields[field.name] = serializers.CharField(
                    label=field.label,
                    required=field_property.required,
                    style={"input_type": "password"},
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.CHECKBOX:
                self.fields[field.name] = serializers.BooleanField(
                    label=field.label, required=field_property.required
                )
            elif field.field_type == FormFieldChoices.DROPDOWN:
                self.fields[field.name] = serializers.ChoiceField(
                    label=field.label,
                    required=field_property.required,
                    choices=[(option, option) for option in field_property.options],
                )
            elif field.field_type == FormFieldChoices.FILE:
                self.fields[field.name] = serializers.FileField(
                    label=field.label, required=field_property.required
                )
            elif field.field_type == FormFieldChoices.NESTED:
                self.fields[field.name] = NestedFormSerializer(
                    nested_form_instance=field.nested_form,
                    field=field,
                    label=field.label,
                    required=field_property.required,
                )

            elif field.field_type == FormFieldChoices.ARRAY:
                self.fields[field.name] = serializers.ListField(
                    child=serializers.CharField(),
                    required=field_property.required,
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.COUNTRY:
                self.fields[field.name] = CountryField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.CURRENCY:
                self.fields[field.name] = MoneyField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                    decimal_places=2,
                    max_digits=10,
                )
            elif field.field_type in [
                FormFieldChoices.DATE,
                FormFieldChoices.DATE_RANGE,
            ]:
                self.fields[field.name] = serializers.DateField(
                    required=field_property.required,
                    validators=field_validators,
                    label=field.label,
                    format="%Y-%m-%d",
                )

            elif field.field_type == FormFieldChoices.TIME:
                self.fields[field.name] = serializers.TimeField(
                    required=field_property.required,
                    validators=field_validators,
                    format="%H:%M:%S",
                )
            elif field.field_type in [
                FormFieldChoices.DATE_TIME,
                FormFieldChoices.DATE_TIME_RANGE,
            ]:
                self.fields[field.name] = serializers.DateTimeField(
                    required=field_property.required,
                    validators=field_validators,
                    format="%Y-%m-%d %H:%M:%S",
                )
            elif field.field_type == FormFieldChoices.EXTERNAL_VALIDATION_ENDPOINT:
                self.fields[field.name] = serializers.CharField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.EXTERNAL_VALIDATION_ENDPOINT:
                field_validators = self.get_validators(
                    field_property.validation_endpoint
                )
                self.fields[field.name] = serializers.CharField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.FLOAT:
                self.fields[field.name] = serializers.FloatField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.INTEGER:
                self.fields[field.name] = serializers.IntegerField(
                    label=field.label,
                    required=field_property.required,
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.UUID:
                self.fields[field.name] = serializers.UUIDField(
                    required=field_property.required,
                    validators=field_validators,
                )
            if field.field_type == FormFieldChoices.RADIO:
                self.fields[field.name] = serializers.ChoiceField(
                    label=field.label,
                    required=field_property.required,
                    choices=[(option, option) for option in field_property.options],
                )
            elif field.field_type == FormFieldChoices.URL:
                self.fields[field.name] = serializers.URLField(
                    required=field_property.required,
                    validators=field_validators,
                )
            elif field.field_type == FormFieldChoices.PHONE_NUMBER:
                self.fields[field.name] = PhoneNumberField(
                    required=field_property.required,
                    validators=field_validators,
                )

    def get_validators(self, validations=[]):  # noqa
        validators = []
        _max_length = "max_length"
        _min_length = "min_length"
        _max_value = "max_value"
        _min_value = "min_value"
        max_length_pattern = rf"{_max_length}:\d+"
        min_length_pattern = rf"{_min_length}:\d+"
        max_value_pattern = rf"{_max_value}:\d+"
        min_value_pattern = rf"{_min_value}:\d+"
        for validation in validations:
            if isinstance(validation, None):
                validators.append(self.resource_validation(validation.url))
            if validation.startswith("data_range"):
                start_date, end_date = validation.split(":")[1].split(",")
                validators.append(self.date_range_validator(start_date, end_date))
            if validation.startswith("time_range"):
                start_time, end_time = validation.split(":")[1].split(",")
                validators.append(self.time_range_validator(start_time, end_time))
            if validation.startswith("datetime_range"):
                start_datetime, end_datetime = validation.split("datetime_range:")[
                    1
                ].split(",")
                validators.append(
                    self.datetime_range_validator(start_datetime, end_datetime)
                )
            if validation.startswith("validation_url"):
                validation_url = validation.split("validation_url:")[1]
                validators.append(self.resource_validation(validation_url))
            if validation.startswith("evaluation_url"):
                evaluation_url = validation.split("evaluation_url:")[1]
                validators.append(self.resource_evaluation(evaluation_url))
            min_length_pattern_checker = self.check_regex(
                min_length_pattern, validation
            )
            max_length_pattern_checker = self.check_regex(
                max_length_pattern, validation
            )
            min_value_pattern_checker = self.check_regex(min_value_pattern, validation)
            max_value_pattern_checker = self.check_regex(max_value_pattern, validation)
            if min_length_pattern_checker:
                min_length_ = int(validation.split(f"{_min_length}:")[1])
                validators.append(MinLengthValidator(min_length_))
            if max_length_pattern_checker:
                max_length_ = int(validation.split(f"{_max_length}:")[1])
                validators.append(MaxLengthValidator(max_length_))
            if min_value_pattern_checker:
                min_value_ = int(validation.split(f"{_min_value}:")[1])
                validators.append(MinValueValidator(min_value_))
            if max_value_pattern_checker:
                max_value_ = int(validation.split(f"{_max_value}:")[1])
                validators.append(MaxValueValidator(max_value_))
        return validators

    def date_range_validator(self, start_date_str, end_date_str):
        def validator(value):
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
            if not (start_date <= value <= end_date):
                raise serializers.ValidationError(
                    f"Date must be between {start_date_str} and {end_date_str}."
                )

        return validator

    def time_range_validator(self, start_time_str, end_time_str):
        def validator(value):
            start_time = time.fromisoformat(start_time_str)
            end_time = time.fromisoformat(end_time_str)
            if not (start_time <= value <= end_time):
                raise serializers.ValidationError(
                    f"Time must be between {start_time_str} and {end_time_str}."
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
                raise serializers.ValidationError(
                    f"DateTime must be between {start_datetime_str} and {end_datetime_str}."
                )

        return validator

    def resource_validation(self, base_url):
        def validator(value):
            if not base_url:
                raise serializers.ValidationError(
                    "Validation service is not configured."
                )
            # Make the request to the validation service
            try:
                response = requests.get(f"{base_url}/{value}")
                if response.status_code != 200:
                    raise serializers.ValidationError(f"Invalid value: {value}")
                else:
                    return True
            except requests.exceptions.RequestException as e:
                raise serializers.ValidationError(
                    f"Error contact admin to validate service: {e}"
                )

        return validator

    def resource_evaluation(self, base_url):
        def validator(value):
            if not base_url:
                raise serializers.ValidationError(
                    "Evaluation service is not configured."
                )
            # Make the request to the validation service
            try:
                response = requests.get(f"{base_url}/{value}")
                if response.status_code != 200:
                    raise serializers.ValidationError(f"Invalid value: {value}")
                else:
                    return True
            except requests.exceptions.RequestException as e:
                raise serializers.ValidationError(
                    f"Error contact admin to evaluate service: {e}"
                )

        return validator

    @property
    def validated_data(self):
        cleaned_data = super().validated_data
        for field_name, field_value in cleaned_data.items():
            field = self.fields.get(field_name)
            if isinstance(field, MoneyField):
                if isinstance(cleaned_data[field_name], Money):
                    cleaned_data[field_name] = {
                        "amount": str(cleaned_data[field_name].amount),
                        "currency": cleaned_data[field_name].currency.code,
                    }
                else:
                    cleaned_data[field_name] = {
                        "amount": cleaned_data[field_name],
                        "currency": None,
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


def build_dynamic_serializer(form_instance):
    return DynamicSerializer, {
        "form_fields": form_instance.fields.all(),
        "form_instance": form_instance,
    }
