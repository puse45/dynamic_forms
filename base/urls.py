from django.urls import path, include
from rest_framework.routers import DefaultRouter

from base.views import ImageSliderViewSet

app_name = "base"

router = DefaultRouter()
router.register(r"image/slider", ImageSliderViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
