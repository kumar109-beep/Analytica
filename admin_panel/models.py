# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.contrib.auth.models import User
# from django.contrib.postgres.fields import JSONField
# from django.contrib.postgres.fields.jsonb import JSONField
# from django_pandas.managers import DataFrameManager

# import datetime
    


# class Asha(models.Model):
#     # index = models.BigIntegerField(blank=True, null=True)
#     age = models.BigIntegerField(blank=True, null=True)
#     asha_id = models.BigIntegerField(blank=True, null=True)
#     block_id = models.BigIntegerField(blank=True, null=True)
#     block_code_census = models.BigIntegerField(blank=True, null=True)
#     block_name = models.TextField(blank=True, null=True)
#     caste = models.TextField(blank=True, null=True)
#     details_of_other_training = models.TextField(blank=True, null=True)
#     district_code_census = models.BigIntegerField(blank=True, null=True)
#     district_name = models.TextField(blank=True, null=True)
#     district_id = models.BigIntegerField(blank=True, null=True)
#     educational_qualification = models.TextField(blank=True, null=True)
#     husband_name = models.TextField(blank=True, null=True)
#     name = models.TextField(blank=True, null=True)
#     population = models.BigIntegerField(blank=True, null=True)
#     region_name = models.TextField(blank=True, null=True)
#     sub_center_id = models.BigIntegerField(blank=True, null=True)
#     sng_id = models.BigIntegerField(blank=True, null=True)
#     state_name = models.TextField(blank=True, null=True)
#     sub_center_name = models.TextField(blank=True, null=True)
#     updated_date = models.TextField(blank=True, null=True)
#     vid = models.TextField(blank=True, null=True)
#     village_name = models.TextField(blank=True, null=True)
#     working_since = models.TextField(blank=True, null=True)
#     age_category = models.TextField(blank=True, null=True)
#     population_category = models.TextField(blank=True, null=True)
#     working_since_year = models.BigIntegerField(blank=True, null=True)
#     mobile_status = models.TextField(blank=True, null=True)

#     objects = DataFrameManager()

#     class Meta:
#         managed = False
#         db_table = 'asha'

# class Sangini(models.Model):
#     age = models.BigIntegerField(blank=True, null=True)
#     sangini_id = models.BigIntegerField(blank=True, null=True)
#     block_id = models.BigIntegerField(blank=True, null=True)
#     block_code_census = models.BigIntegerField(blank=True, null=True)
#     block_name = models.TextField(blank=True, null=True)
#     caste = models.TextField(blank=True, null=True)
#     details_of_other_training = models.TextField(blank=True, null=True)
#     district_code_census = models.BigIntegerField(blank=True, null=True)
#     district_name = models.TextField(blank=True, null=True)
#     district_id = models.BigIntegerField(blank=True, null=True)
#     educational_qualification = models.TextField(blank=True, null=True)
#     husband_name = models.TextField(blank=True, null=True)
#     name = models.TextField(blank=True, null=True)
#     population = models.BigIntegerField(blank=True, null=True)
#     region_name = models.TextField(blank=True, null=True)
#     sub_center_id = models.BigIntegerField(blank=True, null=True)
#     state_name = models.TextField(blank=True, null=True)
#     sub_center_name = models.TextField(blank=True, null=True)
#     updated_date = models.TextField(blank=True, null=True)
#     vid = models.TextField(blank=True, null=True)
#     village_name = models.TextField(blank=True, null=True)
#     working_since = models.TextField(blank=True, null=True)
#     age_category = models.TextField(blank=True, null=True)
#     population_category = models.TextField(blank=True, null=True)
#     working_since_year = models.BigIntegerField(blank=True, null=True)
#     mobile_status = models.TextField(blank=True, null=True)
#     number_of_asha = models.BigIntegerField(blank=True, null=True)
#     mapped_asha = models.TextField(blank=True, null=True)

#     objects = DataFrameManager()

#     class Meta:
#         managed = False
#         db_table = 'sangini'

# class Anm(models.Model):
#     age = models.BigIntegerField(blank=True, null=True)
#     name = models.TextField(blank=True, null=True)
#     anm_id = models.BigIntegerField(blank=True, null=True)
#     block_id = models.BigIntegerField(blank=True, null=True)
#     block_code_census = models.BigIntegerField(blank=True, null=True)
#     block_name = models.TextField(blank=True, null=True)
#     caste = models.TextField(blank=True, null=True)
#     working_since = models.TextField(blank=True, null=True)
#     district_code_census = models.BigIntegerField(blank=True, null=True)
#     district_name = models.TextField(blank=True, null=True)
#     district_id = models.BigIntegerField(blank=True, null=True)
#     job_type = models.TextField(blank=True, null=True)
#     rbid = models.TextField(blank=True, null=True)
#     region_name = models.TextField(blank=True, null=True)
#     sub_center_id = models.BigIntegerField(blank=True, null=True)
#     state_name = models.TextField(blank=True, null=True)
#     stid = models.TextField(blank=True, null=True)
#     sub_center_name = models.TextField(blank=True, null=True)
#     working_since_year = models.BigIntegerField(blank=True, null=True)
#     age_category = models.TextField(blank=True, null=True)
#     mobile_status = models.TextField(blank=True, null=True)
#     number_of_asha = models.BigIntegerField(blank=True, null=True)
#     mapped_asha = models.TextField(blank=True, null=True)

#     objects = DataFrameManager()

#     class Meta:
#         managed = False
#         db_table = 'anm'

# class GeographyLevel(models.Model):
#     name        = models.CharField(max_length=25)
#     is_active   = models.BooleanField(default=True)

# class Geography(models.Model):
#     name        = models.CharField(max_length=25)
#     g_type      = models.ForeignKey(GeographyLevel, on_delete=models.CASCADE)
#     census_code = models.IntegerField(unique=True)
#     latitude    = models.IntegerField() 
#     longitude   = models.IntegerField()
#     is_active   = models.BooleanField(default=True)

# class Caste(models.Model):
#     name = models.CharField(max_length=25)
#     is_active   = models.BooleanField(default=True)

# class Education(models.Model):
#     name        = models.CharField(max_length=25)
#     is_active   = models.BooleanField(default=True)

# class ASHA(models.Model):
#     age             = models.IntegerField()                                                 
#     asha_id         = models.IntegerField()                                             
#     caste           = models.ForeignKey(Caste, on_delete=models.CASCADE)
#     education       = models.ForeignKey(Education, on_delete=models.CASCADE)                  
#     husband_name    = models.CharField(max_length=25)                                                        
#     name            = models.CharField(max_length=25)                                                        
#     population      = models.IntegerField()                                                                                       
#     village         = models.ForeignKey(Geography, on_delete=models.CASCADE)                                                     
#     joining_date    = models.DateField(default=datetime.date.today)                                                   
#     mobile          = models.IntegerField()

