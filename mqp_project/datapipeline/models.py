from django.db import models
from django.conf import settings


# Create your models here.
class Study(models.Model):
    study_id = models.AutoField(primary_key = True)
    study_name = models.CharField(max_length=255, null=True, blank=True)
    study_description = models.TextField(null=True, blank=True) 
    is_irb_approved = models.BooleanField(null=True, blank=True)
    institutions_involved = models.TextField(null=True, blank=True)
    study_start_date = models.DateField(null=True, blank=True) 
    study_end_date = models.DateField(null=True, blank=True)
    study_contact = models.CharField(max_length=255, null=True, blank=True)
    study_notes = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    visibility = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = "study"  
    
    
class StudyGroup(models.Model):
    study_group_id = models.AutoField(primary_key=True)
    study_group_name = models.CharField(max_length=255, null=True, blank=True)
    study_group_description = models.TextField(null=True, blank=True) 
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "studygroup"  
    
    
class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_number = models.CharField(max_length=255, null=True, blank=True) 
    study_group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "subject"  
    
    
class DataCategory(models.Model):
    data_category_id = models.AutoField(primary_key=True)
    data_category_name = models.CharField(max_length=255, null=True, blank=True)
    is_time_series = models.BooleanField(null=True, blank=True) 
    has_subject_name = models.BooleanField(null=True, blank=True)
    subject_organization = models.CharField(max_length=255, null=True, blank=True)
    dc_table_name = models.CharField(max_length=255, null=True, blank=True)
    dc_description = models.TextField(null=True, blank=True) 
    
    class Meta:
        db_table = "datacategory"  
    
    
class DataCategoryStudyXref(models.Model):
    dc_study_id = models.AutoField(primary_key=True)
    data_category = models.ForeignKey(DataCategory, on_delete=models.CASCADE)
    study = models.ForeignKey(Study, on_delete=models.CASCADE)
    dc_table_name = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        db_table = "datacategorystudyxref"  
  
  
class Attribute(models.Model):
    attr_id = models.AutoField(primary_key=True)
    attr_name = models.CharField(max_length=255, null=True, blank=True)
    attr_description = models.CharField(max_length=255, null=True, blank=True)
    data_type = models.CharField(max_length=255, null=True, blank=True)
    unit = models.CharField(max_length=255, null=True, blank=True)
    device_name = models.CharField(max_length=255, null=True, blank=True)
    data_category = models.ForeignKey(DataCategory, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "attribute"