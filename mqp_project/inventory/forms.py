from django import forms

# Search form for finding studies with specific metadata
class StudySearchForm(forms.Form):
    searchTerm = forms.CharField(label='Search for studies that contain the following search term in any of the metadata below:', required=False)
    studyName = forms.BooleanField(label='Study Name', required=False, initial=True)
    studyDescription = forms.BooleanField(label='Study Description', required=False, initial=True)
    institutionsInvolved = forms.BooleanField(label='Institutions Involved', required=False, initial=True)
    studyContact = forms.BooleanField(label='Study Contact', required=False, initial=True)
    studyNotes = forms.BooleanField(label='Study Notes', required=False, initial=True)
    dataCategory = forms.BooleanField(label='Data Category', required=False, initial=True)