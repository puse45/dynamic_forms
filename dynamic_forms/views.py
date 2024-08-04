from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from dynamic_forms.models import Form
from dynamic_forms.serializers import FormSerializer
from dynamic_forms.utils import build_dynamic_form


class FormDetailView(generics.RetrieveAPIView):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    lookup_field = "slug"


class FormSubmissionView(generics.GenericAPIView):
    lookup_field = "slug"

    def post(self, request, *args, **kwargs):
        form_instance = get_object_or_404(Form, slug=kwargs["slug"])
        form_class, form_kwargs = build_dynamic_form(form_instance)
        form = form_class(data=request.data, files=request.FILES, **form_kwargs)
        if form.is_valid():
            return Response(
                {"success": True, "data": form.cleaned_data}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"success": False, "errors": form.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
