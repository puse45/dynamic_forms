from rest_framework import serializers
from dynamic_forms.models import Form, Field, FieldProperty


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = ["name", "field_type", "label", "nested_form"]


class FormFieldPropertiesSerializer(serializers.ModelSerializer):
    nested_form = serializers.SerializerMethodField()

    class Meta:
        model = FieldProperty
        fields = [
            "name",
            "field_type",
            "label",
            "options",
            "required",
            "validation",
            "style",
            "hidden",
            "index",
            "nested_form",
        ]

    def get_nested_form(self, obj):
        nest = obj.field.nested_form
        if nest:
            return FormSerializer(nest).data


class FormSerializer(serializers.ModelSerializer):
    fields = FormFieldPropertiesSerializer(many=True, source="get_form_field_property")

    class Meta:
        model = Form
        fields = ["id", "name", "slug", "fields"]
