from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from dynamic_forms.models import Form
from dynamic_forms.serializers import FormSerializer
from dynamic_forms.utils import build_dynamic_serializer, DynamicSerializer


class FormDetailView(generics.RetrieveAPIView):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    lookup_field = "slug"


class FormSubmissionView(generics.GenericAPIView):
    lookup_field = "slug"
    erializer_class = DynamicSerializer

    def post(self, request, *args, **kwargs):
        form_instance = get_object_or_404(Form, slug=kwargs["slug"])
        serializer_class, form_kwargs = build_dynamic_serializer(form_instance)
        serializer_fields = form_kwargs.pop("form_fields")
        serializer = serializer_class(
            data=request.data,
            form_fields=serializer_fields,
            form_instance=form_instance,
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
