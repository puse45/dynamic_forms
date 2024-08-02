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


class Countable(models.Model):
    id = models.AutoField(primary_key=True)
    counter = models.PositiveSmallIntegerField(default=1)

    class Meta:
        abstract = True

    @property
    def next_number(self):
        self.counter += 1
        self.save()
        return self.counter
