from rest_framework import serializers
from dynamic_forms.models import Form, FormField


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = [
            "name",
            "field_type",
            "label",
            "required",
            "validation",
            "options",
            "hidden",
        ]


class FormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True)

    class Meta:
        model = Form
        fields = ["id", "name", "fields"]
