from django import forms

class StudyNameForm(forms.Form):
    studyName = forms.CharField(label='Study Name', required=True)
    
class UploaderInfoForm(forms.Form):
    groupName = forms.CharField(label='Study Group Name', required=False)
    categoryName = forms.CharField(label='Data Category Name', required=True)
    
    SUBJECT_CHOICES = [('file', ('Subject per File')), ('row', 'Subject per Row')]
    
    subjectOrganization = forms.ChoiceField(choices=SUBJECT_CHOICES, widget=forms.RadioSelect, label="What Format Does this Data Category Follow?", required=True)
    
    TIME_SERIES_CHOICES = [('y', 'Yes'), ('n', 'No')]
    
    isTimeSeries = forms.ChoiceField(choices=TIME_SERIES_CHOICES, widget=forms.RadioSelect, label="Is this Data Category Time Series?", required=True)
    
    uploadedFiles = forms.FileField(label="Select Files", required=True, widget=forms.ClearableFileInput(attrs={'multiple': True}))
    

class UploadInfoCreationForm(forms.Form):
    YES_NO_CHOICES = [('y', 'Yes'), ('n', 'No')]
    
    subjectLabel = "Is the subject name or ID included in the file? Note that it must be the first column"
    hasSubjectID = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect, label=subjectLabel, required=False)
    
    nameOfValueMeasured = forms.CharField(label='What is the name of the value being measured in this time series?', required=False)
    
    allowed_datatypes = [
        (1, 'String/text'),
        (2, 'Integer'),
        (3, 'Float/Decimal'),
        (4, 'Datetime'),
        (5, 'Boolean')
    ]
    
    datatypeOfMeasured = forms.CharField(label='What is the Data Type?', widget=forms.Select(choices=allowed_datatypes), required=False)
    
    studyGroupDescription = forms.CharField(label='Study Group Descrption', required=False)
    
    dataCategoryDescription = forms.CharField(label='Data Category Descrption', required=False)
    
    def __init__(self, *args, **kwargs):
        extra = kwargs.pop('dynamicFields')
        allowed_datatypes = [
            (1, 'String/text'),
            (2, 'Integer'),
            (3, 'Float/Decimal'),
            (4, 'Datetime'),
            (5, 'Boolean')
        ]
        super(UploadInfoCreationForm, self).__init__(*args, **kwargs) 
        
        for name in extra:
            fieldName = name
            
            dataType = '{}_custom_dataType'.format(fieldName)
            description = '{}_custom_description'.format(fieldName)
            unit = '{}_custom_unit'.format(fieldName) 
            deviceUsed = '{}_custom_deviceUsed'.format(fieldName)
            
            self.fields[dataType] = forms.CharField(label='What is the Data Type of {}?'.format(fieldName), widget=forms.Select(choices=allowed_datatypes), required=True)
            self.fields[description] = forms.CharField(label='Description of {}'.format(fieldName), required=True)
            self.fields[unit] = forms.CharField(label='Unit of {} (if aplicable)'.format(fieldName), required=False)
            self.fields[deviceUsed] = forms.CharField(label='Device Used to Measure {} (if applicable)'.format(fieldName), required=False)
    
    def getAllFields(self):
        for name, value in self.cleaned_data.items():
            yield (name, value)
            
    def getExtraFields(self):
        for name, value in self.cleaned_data.items():
            if '_custom_' in name:
                yield (name, value)
            
    def reset(self):
        for field in self.fields:
            self.fields[field].required = False
            
class UploadPositionForm(forms.Form) :
    
    def __init__(self, *args, **kwargs):
        columns = kwargs.pop('columns')
        
        size = len(columns)
        
        available_positions = [(i, i) for i in range(size)]
        
        allowed_datatypes = [
            (1, 'String/text'),
            (2, 'Integer'),
            (3, 'Float/Decimal'),
            (4, 'Datetime'),
            (5, 'Boolean')
        ]
        
        super(UploadPositionForm, self).__init__(*args, **kwargs) 
        
        for column in columns:
            position = '{}_custom_position'.format(column)
            dataType = '{}_custom_dataType'.format(column)
            
            self.fields[position] = forms.CharField(label="{}'s Position: ".format(column), widget=forms.Select(choices=available_positions, attrs={'id': 'mySelection'}), required=True)
            self.fields[dataType] = forms.CharField(label='Datatype:', widget=forms.Select(choices=allowed_datatypes, attrs={'id': 'mySelection'}), required=True)
    
    def getColumnFields(self):
        for name, value in self.cleaned_data.items():
            yield (name, value)
        
        
        
        
        
            
    
            
    
    
