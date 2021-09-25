# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.contrib.auth.models import User

class Dataframe(models.Model):
    name        = models.CharField(max_length=150, blank=True, null=True)
    rows        = models.IntegerField(default=-1)
    meta        = JSONField(blank=True, null=True)
    path        = models.CharField(max_length=150, blank=True, null=True)
    schema_hash = models.CharField(max_length=32, blank=True, null=True)
    user        = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)


class Frame_edit_request(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    frame       = models.ForeignKey(Dataframe, on_delete=models.CASCADE)
    col_name    = models.TextField(blank=True, null=True)
    old_val     = models.TextField(blank=True, null=True)
    new_val     = models.TextField(blank=True, null=True)
    hash_code   = models.CharField(max_length=150, blank=True, null=True)
    verified    = models.NullBooleanField()
    comment     = models.CharField(max_length=150, blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)