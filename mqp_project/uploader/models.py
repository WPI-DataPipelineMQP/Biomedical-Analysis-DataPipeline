from django.db import models
from datapipeline.models import DataCategory

# Create your models here.

# Table to link the name of an uploaded file to its corresponding data category, only used in upload process
class Document(models.Model):
    filename = models.CharField(max_length=250)                                 # Name of file uploaded
    data_category = models.ForeignKey(DataCategory, on_delete=models.CASCADE)   # Foreign key to data category that file data will be contained in
    
    class Meta:
        db_table = "document"
        managed = True

