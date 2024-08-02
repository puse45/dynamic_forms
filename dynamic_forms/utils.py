from django import forms

from dynamic_forms.choices import FormFieldChoices
from django.core.validators import MinLengthValidator, MaxLengthValidator


class DynamicForm(forms.Form):
    def __init__(self, *args, **kwargs):
        form_fields = kwargs.pop("form_fields")
        super(DynamicForm, self).__init__(*args, **kwargs)
        for field in form_fields:
            if field.field_type == FormFieldChoices.TEXT:
                self.fields[field.field.name] = forms.CharField(
                    label=field.field.label,
                    required=field.required,
                    validators=self.get_validators(field.validation),
                )
            elif field.field_type == FormFieldChoices.EMAIL:
                self.fields[field.field.field.name] = forms.EmailField(
                    label=field.field.label,
                    required=field.required,
                    validators=self.get_validators(field.validation),
                )
            elif field.field_type == FormFieldChoices.PASSWORD:
                self.fields[field.field.name] = forms.CharField(
                    label=field.field.label,
                    required=field.required,
                    widget=forms.PasswordInput,
                    validators=self.get_validators(field.validation),
                )
            elif field.field_type == FormFieldChoices.CHECKBOX:
                self.fields[field.field.name] = forms.BooleanField(
                    label=field.field.label, required=field.required
                )
            elif field.field_type == FormFieldChoices.DROPDOWN:
                self.fields[field.field.name] = forms.ChoiceField(
                    label=field.field.label,
                    required=field.required,
                    choices=[(option, option) for option in field.options],
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
