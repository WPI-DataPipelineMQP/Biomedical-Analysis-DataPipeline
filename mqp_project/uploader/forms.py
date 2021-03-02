from django import forms
from functools import partial
from django.utils.safestring import mark_safe

from datapipeline.models import Study, StudyGroup, DataCategory, DataCategoryStudyXref

from .viewHelpers import Helper, DBFunctions


class StudyNameForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        all_studies = kwargs.pop('studies')
        
        super(StudyNameForm, self).__init__(*args, **kwargs)
        
        YES_NO = [('y', 'Yes'), ('n', 'No')]
    
        if len(all_studies) > 0: 
            self.fields['existingStudies'] = forms.CharField(label='Existing Studies:',
                                              widget=forms.Select(choices=all_studies),
                                              required=False)
    
            self.fields['otherStudy'] = forms.CharField(label='Other Study Name:', required=False)
        
            self.fields['which_study_field'] = forms.ChoiceField(choices=YES_NO,
                                                  widget=forms.RadioSelect(attrs={'required': 'required'}),
                                                  label="Did you choose an existing study name?")
        
        else:
            self.fields['otherStudy'] = forms.CharField(label='Enter a Study Name:', required=True)


class StudyInfoForm(forms.Form):
    YES_NO_CHOICES = [(1, 'Yes'), (0, 'No')]
    VISIBILITY_CHOICES = [('Public', 'Public'), ('Private', 'Private')]
    DateInput = partial(forms.DateInput, {'class': 'datepicker'})
    studyDescription = forms.CharField(
        label='Study Description', required=True)
    isIRB_Approved = forms.ChoiceField(choices=YES_NO_CHOICES, widget=forms.RadioSelect(
        attrs={'required': 'required'}), label="Is study IRB approved?")
    institutions = forms.CharField(
        label="Institutions Involved (separate by comma if multiple)", required=False)
    startDate = forms.DateField(
        widget=DateInput(), label="Study Start Date", required=True)
    endDate = forms.DateField(
        widget=DateInput(), label="Study End Date", required=True)
    contactInfo = forms.CharField(label='Study Contact Info', required=False)
    visibility = forms.ChoiceField(choices=VISIBILITY_CHOICES, widget=forms.RadioSelect(
        attrs={'required': 'required'}), label="Visibility")
    notes = forms.CharField(label='Study Notes',
                            widget=forms.Textarea, required=False)


class UploaderInfoForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        YES_NO = [('y', 'Yes'), ('n', 'No')]
        
        SUBJECT_CHOICES = [('file', 'Subject per File'), ('row',
                                                      'Subject per Row'), ('column', 'Subject per Column')]
        
        DUPLICATE_CHOICES = [('replace', 'Replace Duplicates'), ('append',
                                                             'Add Duplicates'), ('newFile', 'Try Different File(s)')]
        studyID = kwargs.pop('id')
        
        super(UploaderInfoForm, self).__init__(*args, **kwargs)
        
        groupsExist = StudyGroup.objects.filter(study=studyID)
        
        studyGroups, dataCategories = [], []
        
        if groupsExist:
            groupObjs = StudyGroup.objects.filter(study=studyID)
            
            studyGroups = [(obj.study_group_name, obj.study_group_name) for obj in groupObjs]
            
            foundCategories = DBFunctions.getAllDataCategoriesOfStudy(studyID)
            
            dataCategories = [(name, name) for name in foundCategories]
        
        if len(dataCategories) == 0:
            self.fields['categoryName'] = forms.CharField(label='Data Category Name', required=True)
        else:
            self.fields['existingCategory'] = forms.CharField(label='Existing Data Categories:',
                                                    widget=forms.Select(choices=dataCategories),
                                                    required=False)
            
            self.fields['categoryName'] = forms.CharField(label='Other Data Category Name', required=False)
            
            self.fields['which-category-field'] = forms.ChoiceField(choices=YES_NO,
                                            widget=forms.RadioSelect(attrs={'required': 'required'}), label="Did you choose an existing data category?")
        
        if len(studyGroups) == 0:
            self.fields['groupName'] = forms.CharField(label='Study Group Name', required=False)
            
        else:
            self.fields['existingStudyGroup'] = forms.CharField(label='Existing Study Groups:',
                                                    widget=forms.Select(choices=studyGroups),
                                                    required=False)
            
            self.fields['groupName'] = forms.CharField(label='Other Study Group Name', required=False)
            
            self.fields['which-group-field'] = forms.ChoiceField(choices=YES_NO,
                                            widget=forms.RadioSelect(attrs={'required': 'required'}), label="Did you choose an existing study group?")
            
        self.fields['subjectOrganization'] = forms.ChoiceField(choices=SUBJECT_CHOICES,
                                            widget=forms.RadioSelect(attrs={'required': 'required'}), label="What Format Does this Data Category Follow?")
        
        self.fields['isTimeSeries'] = forms.ChoiceField(choices=YES_NO,
                                     widget=forms.RadioSelect(attrs={'required': 'required'}), label="Is this Data Category Time Series?")
        
        self.fields['handleDuplicate'] = forms.ChoiceField(choices=DUPLICATE_CHOICES,
                                        widget=forms.RadioSelect(attrs={'class': 'duplicate'}), 
                                        label=mark_safe("<mark>Handling Duplicate Options (<strong>Please Select One of the Options</strong>)</mark>"),
                                        required=False)
        
        self.fields['uploadedFiles'] = forms.FileField(label="Select Files", required=True, widget=forms.ClearableFileInput(attrs={'multiple': True}))
    


class UploadInfoCreationForm(forms.Form):
    YES_NO_CHOICES = [('y', 'Yes'), ('n', 'No')]

    subjectLabel = mark_safe("Is the subject name or ID included in the file?* <strong>Note that it must be the first column</strong>")
    hasSubjectID = forms.ChoiceField(
        choices=YES_NO_CHOICES, widget=forms.RadioSelect, label=subjectLabel, required=False)

    nameOfValueMeasured = forms.CharField(
        label='What is the name of the value being measured in this time series?', required=False)

    allowed_datatypes = [
        (1, 'String / Text'),
        (2, 'Integer'),
        (3, 'Float / Decimal'),
        (4, 'Datetime'),
        (5, 'Boolean')
    ]

    #datatypeOfMeasured = forms.CharField(label='What is the Data Type?', widget=forms.Select(choices=allowed_datatypes), required=False)

    studyGroupDescription = forms.CharField(
        label='Study Group Description', required=False)

    dataCategoryDescription = forms.CharField(
        label='Data Category Description', required=False)

    def __init__(self, *args, **kwargs):
        extra = kwargs.pop('dynamicFields')
        allowed_datatypes = [
            (1, 'String / Text'),
            (2, 'Integer'),
            (3, 'Float / Decimal'),
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

            self.fields[dataType] = forms.CharField(label='What is the Data Type of {}?'.format(
                fieldName), widget=forms.Select(choices=allowed_datatypes), required=True)
            self.fields[description] = forms.CharField(
                label='Description of {}'.format(fieldName), required=True)
            self.fields[unit] = forms.CharField(
                label='Unit of {} (if applicable)'.format(fieldName), required=False)
            self.fields[deviceUsed] = forms.CharField(
                label='Device Used to Measure {} (if applicable)'.format(fieldName), required=False)

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


class UploadPositionForm(forms.Form):

    def __init__(self, *args, **kwargs):
        columns = kwargs.pop('columns')

        size = len(columns)

        available_positions = [(i, i) for i in range(size)]

        super(UploadPositionForm, self).__init__(*args, **kwargs)

        for i, column in enumerate(columns):
            position = '{}_custom_position'.format(column)

            self.fields[position] = forms.CharField(label="{}'s Position: ".format(column),
                                                    widget=forms.Select(choices=available_positions, attrs={
                                                                        'id': 'mySelection'}),
                                                    required=True,
                                                    initial=i)


    def getColumnFields(self):
        for name, value in self.cleaned_data.items():
            yield (name, value)



class DisabledInputForm(forms.Form):
    files = forms.CharField(widget=forms.TextInput({
        'class': 'form-control',
        'readonly': True
    }))
