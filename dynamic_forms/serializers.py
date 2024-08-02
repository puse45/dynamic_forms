from rest_framework import serializers
from dynamic_forms.models import Form, FormField, Field, FormFieldsOrder


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = [
            "name",
            "field_type",
            "label",
        ]


class FormFieldsOrderIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFieldsOrder
        fields = ["index"]


class FormFieldSerializer(serializers.ModelSerializer):
    field = FieldSerializer()
    index = FormFieldsOrderIndexSerializer(many=True, source="form_field_orders")

    class Meta:
        model = FormField
        fields = ["field", "required", "validation", "options", "hidden", "index"]


class FormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True)

    class Meta:
        model = Form
        fields = ["id", "name", "slug", "fields"]
