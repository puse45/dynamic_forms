import uuid
from django.db import models
from timestampedmodel import TimestampedModel
from base.managers import BaseManager


class BaseModel(TimestampedModel):
    id = models.UUIDField(
        primary_key=True, editable=False, default=uuid.uuid4, db_index=True
    )
    slug = models.SlugField(unique=True, db_index=True, max_length=255, blank=True)
    is_archived = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, null=True, blank=True)

    objects = BaseManager()

    class Meta:
        abstract = True
        ordering = ("-updated_at", "-created_at")
        get_latest_by = ("updated_at",)
