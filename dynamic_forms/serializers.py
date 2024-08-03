from rest_framework import serializers
from dynamic_forms.models import Form, Field, FieldProperty


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = [
            "name",
            "field_type",
            "label",
        ]


class FieldPropertySerializer(serializers.ModelSerializer):
    options = serializers.JSONField(allow_null=True, default=list)
    validation = serializers.JSONField(allow_null=True, default=list)
    hidden = serializers.BooleanField(default=False)
    required = serializers.BooleanField(default=False)
    index = serializers.IntegerField(default=0)
    style = serializers.CharField(default="")

    class Meta:
        model = FieldProperty
        fields = [
            "required",
            "style",
            "validation",
            "options",
            "hidden",
            "index",
            "name",
            "field_type",
            "label",
        ]


class FormSerializer(serializers.ModelSerializer):
    fields = FieldPropertySerializer(many=True)

    class Meta:
        model = Form
        fields = ["id", "name", "slug", "fields"]
