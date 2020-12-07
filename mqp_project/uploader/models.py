from django.db import models
from datapipeline.models import DataCategory

# Create your models here.

class Document(models.Model):
    filename = models.CharField(max_length=250)
    data_category = models.ForeignKey(DataCategory, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "Document"