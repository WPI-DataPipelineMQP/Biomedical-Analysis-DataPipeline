from django.db import models

# Create your models here.
class Document(models.Model):
    uploadedFile = models.FileField(upload_to='uploaded_csvs')
    filename = models.CharField(max_length=250)
