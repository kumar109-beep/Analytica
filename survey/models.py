from django.db import models


class GeographyLevel(models.Model):
    name            = models.CharField(max_length=50, unique=True)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    
class Geography(models.Model):
    name            = models.CharField(max_length=150)
    GeographyLevel  = models.ForeignKey(GeographyLevel, on_delete=models.CASCADE)
    census_code     = models.IntegerField(blank=True, null=True)
    Geography       = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    latitude        = models.FloatField(blank=True, null=True) 
    longitude       = models.FloatField(blank=True, null=True)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)


class Survey(models.Model):
    name            = models.CharField(max_length=255) 
    version         = models.IntegerField(blank=True, null=True)
    start_session   = models.DateField(blank=True, null=True)   
    end_session     = models.DateField(blank=True, null=True)   
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

class SurveyToGeography(models.Model):
    Survey          = models.ForeignKey(Survey, on_delete=models.CASCADE) 
    Geography       = models.ForeignKey(Geography, on_delete=models.CASCADE)  
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

class Category(models.Model):
    name            = models.TextField()
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

class Indicator(models.Model):
    name            = models.TextField()
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    
class IndicatorToSurveyToGeography(models.Model):
    Indicator           = models.ForeignKey(Indicator, on_delete=models.CASCADE) 
    Category            = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    SurveyToGeography   = models.ForeignKey(SurveyToGeography, on_delete=models.CASCADE) 
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

class Attribute(models.Model):
    name        = models.CharField(max_length=255)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

class AttributeToIndicatorToSurveyToGeography(models.Model):
    IndicatorToSurveyToGeography    = models.ForeignKey(IndicatorToSurveyToGeography, on_delete=models.CASCADE)
    Attribute                       = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    created_at                      = models.DateTimeField(auto_now_add=True)
    updated_at                      = models.DateTimeField(auto_now=True)

class Answer(models.Model):
    AttributeToIndicatorToSurveyToGeography = models.ForeignKey(AttributeToIndicatorToSurveyToGeography, on_delete=models.CASCADE)
    value                                   = models.CharField(max_length=100, null=True, blank=True)
    created_at                              = models.DateTimeField(auto_now_add=True)
    updated_at                              = models.DateTimeField(auto_now=True)