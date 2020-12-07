from django.db import models
from datapipeline.models import DataCategory

# Create your models here.

class Document(models.Model):
<<<<<<< HEAD
    filename = models.CharField(max_length=250)
    data_category = models.ForeignKey(DataCategory, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "Document"
=======
    uploadedFile = models.FileField(upload_to='uploaded_csvs')
    filename = models.CharField(max_length=250)
>>>>>>> 285e50c0a097a06cd25253eb41406aa71e218740
