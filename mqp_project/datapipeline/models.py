from django.db import models
from django import forms

# Create your models here.
class Studies:
    field = forms.BooleanField()

class DataCategories:
	field = forms.BooleanField()

class StudyGroups:
	field = forms.BooleanField()


class Document(models.Model):
    uploadedFile = models.FileField(upload_to='uploaded_csvs')
    filename = models.CharField(max_length=250)

