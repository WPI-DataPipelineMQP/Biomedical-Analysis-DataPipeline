from django import forms

# Search form for finding studies with a specific data category
class DataCategorySearchForm(forms.Form):
    searchTerm = forms.CharField(label='Find studies that contain a specific data category', required=False)