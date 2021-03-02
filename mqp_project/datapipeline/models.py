from django.db import models
from django.conf import settings


# Create your models here.

# Table to contain uploaded studies and their metadata
class Study(models.Model):
    study_id = models.AutoField(primary_key = True)                                         # Primary key
    study_name = models.CharField(max_length=255, null=True, blank=True)                    # Name of study
    study_description = models.TextField(null=True, blank=True)                             # Description of study
    is_irb_approved = models.BooleanField(null=True, blank=True)                            # Boolean indicating whether study is IRB approved
    institutions_involved = models.TextField(null=True, blank=True)                         # Institutions involved in study
    study_start_date = models.DateField(null=True, blank=True)                              # Date that study was started, uses date type
    study_end_date = models.DateField(null=True, blank=True)                                # Date that study ended, uses date type
    study_contact = models.CharField(max_length=255, null=True, blank=True)                 # Contact information (likely an email) to get in touch with owner of study
    study_notes = models.TextField(null=True, blank=True)                                   # Miscellaneous notes to include about study
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)# Foreign key to user in auth_user table that uploaded the study
    visibility = models.TextField(null=True, blank=True)                                    # String indicating if users other than owner can see a study.
                                                                                                # Expected values = {"Private", "Public", "Public (Testing)"}
    
    class Meta:
        db_table = "study"  
    
# Table to contain groups of subjects within a study (ex: Control, experimental, ect.)
class StudyGroup(models.Model):
    study_group_id = models.AutoField(primary_key=True)                                     # Primary key
    study_group_name = models.CharField(max_length=255, null=True, blank=True)              # Name of study group
    study_group_description = models.TextField(null=True, blank=True)                       # Description of study group
    study = models.ForeignKey(Study, on_delete=models.CASCADE)                              # Foreign key to study that study group is a part of
    
    class Meta:
        db_table = "studygroup"  
    
# Table to contain test subjects/participants within a study
class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)                                         # Primary key
    subject_number = models.CharField(max_length=255, null=True, blank=True)                # String identifier for subject, assuming subjects will be anonymized
    study_group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE)                   # Foreign key to study group that subject is a part of
    
    class Meta:
        db_table = "subject"  
    
# Table to contain uploaded data categories (collections of thematically similar attributes that would be in a spreadsheet together)
class DataCategory(models.Model):
    data_category_id = models.AutoField(primary_key=True)                                   # Primary key
    data_category_name = models.CharField(max_length=255, null=True, blank=True)            # Name of data category. This must be unique for data categories within the same study
    is_time_series = models.BooleanField(null=True, blank=True)                             # Boolean indicating whether or not the data category is a time series
    has_subject_name = models.BooleanField(null=True, blank=True)                           # Boolean related to "Subject per row" and "Subject per column" formats that indicates if
                                                                                                # the subject name is explicitly included in the spreadsheets
    subject_organization = models.CharField(max_length=255, null=True, blank=True)          # String indicating the input format of the data category. This is related to whether each
                                                                                                # file contains data about a single subject or multiple.
                                                                                                # Expected values = {"file", "row", "column"}
    dc_table_name = models.CharField(max_length=255, null=True, blank=True)                 # Name of database table related to this data category. Note that this would be a
                                                                                                # dynamically created table that can not be mapped out as a Django model.
                                                                                                # The name scheme of the tables is
                                                                                                # "<data_category_name>_<study_id of first study to use this data category>".
    dc_description = models.TextField(null=True, blank=True)                                # Description of data category
    
    class Meta:
        db_table = "datacategory"  
    
# Table to model many-to-many relationship between data categories and studies. Could likely be replaced using Django's built-in many-to-many field
class DataCategoryStudyXref(models.Model):
    dc_study_id = models.AutoField(primary_key=True)                                        # Primary key
    data_category = models.ForeignKey(DataCategory, on_delete=models.CASCADE)               # Foreign key to data category
    study = models.ForeignKey(Study, on_delete=models.CASCADE)                              # Foreign key to study
    dc_table_name = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        db_table = "datacategorystudyxref"  
  
# Table to contain metadata about the attributes of each data category. Each column from dynamically created table (other than the pks and fks) would have an entry in the Attribute table)
class Attribute(models.Model):
    attr_id = models.AutoField(primary_key=True)                                            # Primary key
    attr_name = models.CharField(max_length=255, null=True, blank=True)                     # Name of attribute, extracted from the column/row name in the uploaded files
    attr_description = models.CharField(max_length=255, null=True, blank=True)              # Description of attribute
    data_type = models.CharField(max_length=255, null=True, blank=True)                     # SQL data type of the attribute
    unit = models.CharField(max_length=255, null=True, blank=True)                          # Name of the unit for the attribute
    device_name = models.CharField(max_length=255, null=True, blank=True)                   # Name of the device used to measure the attribute
    data_category = models.ForeignKey(DataCategory, on_delete=models.CASCADE)               # Foreign key to data category that contains the attribute
    
    class Meta:
        db_table = "attribute"