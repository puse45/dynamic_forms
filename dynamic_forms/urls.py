from django.urls import path
from dynamic_forms.views import FormDetailView, FormSubmissionView

urlpatterns = [
    path("forms/<slug:slug>/", FormDetailView.as_view(), name="form_detail"),
    path(
        "forms/<slug:slug>/submit/",
        FormSubmissionView.as_view(),
        name="form_submission",
    ),
]
