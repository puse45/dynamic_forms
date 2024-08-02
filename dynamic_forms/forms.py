import re

from django import forms
from django.utils.translation import gettext_lazy as _

from dynamic_forms.choices import FormFieldChoices
from dynamic_forms.models import FormField

validation_pattern = r"(\w+:\w+|\w+)"


class FormFieldForm(forms.ModelForm):
    class Meta:
        model = FormField
        exclude = ["created_at", "updated_at"]

    def clean(self):
        field = self.cleaned_data.get("field")
        required = self.cleaned_data.get("required")
        validation = self.cleaned_data.get("validation")
        options = self.cleaned_data.get("options")
        hidden = self.cleaned_data.get("hidden")

        if field.field_type == FormFieldChoices.DROPDOWN and not options:
            raise forms.ValidationError({"options": _("Options are required.")})
        if required and hidden:
            raise forms.ValidationError(
                {"required": _("Required cannot be True if Hidden is True.")}
            )
        if validation:
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
