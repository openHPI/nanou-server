from django.contrib.auth.models import User
from django.db import models


class Survey(models.Model):
    watch_minimum = models.PositiveSmallIntegerField()
    link = models.URLField()
    secondary_link = models.URLField(blank=True, null=True)
    completed_by = models.ManyToManyField(User, related_name='completed_surveys')
