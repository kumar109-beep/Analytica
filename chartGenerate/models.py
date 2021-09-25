from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
from django.core.validators import MaxValueValidator, MinValueValidator
from dataframe.models import Dataframe


class Chartconfig(models.Model):
    conf        = JSONField(blank=True, null=True)
    frame       = models.ForeignKey(Dataframe, on_delete=models.CASCADE, blank=True, null=True)
    about       = models.TextField(blank=True, null=True)