from django import forms

from dynamic_forms.choices import FormFieldChoices
from django.core.validators import MinLengthValidator, MaxLengthValidator
from secrets import compare_digest


class NestedFormField(forms.Field):
    def __init__(self, nested_form_instance, *args, **kwargs):
        self.nested_form_instance = nested_form_instance
        super().__init__(*args, **kwargs)

    def clean(self, value):
        if value is None:
            value = {}
        # if not isinstance(value, dict):
        #     raise forms.ValidationError("Invalid data for nested form")
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
        super(DynamicForm, self).__init__(*args, **kwargs)
        for field in form_fields:
            field_property = field.form_field_property.first()
            if field.field_type == FormFieldChoices.TEXT:
                self.fields[field.name] = forms.CharField(
                    label=field.label,
                    required=field_property.required,
                    validators=self.get_validators(field_property.validation),
                )
            elif field.field_type == FormFieldChoices.EMAIL:
                self.fields[field.name] = forms.EmailField(
                    label=field.label,
                    required=field_property.required,
                    validators=self.get_validators(field_property.validation),
                )
            elif compare_digest(field.field_type, FormFieldChoices.PASSWORD):
                self.fields[field.name] = forms.CharField(
                    label=field.label,
                    required=field_property.required,
                    widget=forms.PasswordInput,
                    validators=self.get_validators(field_property.validation),
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

    def get_validators(self, validations):
        # Add validation logic here
        validators = []
        for validation in validations:
            if validation.startswith("min_length"):
                min_length = int(validation.split(":")[1])
                validators.append(MinLengthValidator(min_length))
            if validation.startswith("max_length"):
                max_length = int(validation.split(":")[1])
                validators.append(MaxLengthValidator(max_length))
        return validators


def build_dynamic_form(form_instance):
    return DynamicForm, {"form_fields": form_instance.fields.all()}
