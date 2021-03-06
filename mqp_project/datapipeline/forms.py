from django import forms

#symbols used in filter form
#for numbers and datetimes
Integer_Symbols = [
    ('', None),
    ('equal', '='),
    ('notequal', '!='),
    ('less', '<'),
    ('greater', '>'),
    ('lessorequal', '<='),
    ('greaterorequal', '>='),
]
#for other data types
NonInteger_Symbols = [
    ('equal', '='),
    ('notequal', '!='),
]

# Dynamic form that uses customFields arg to create boolean fields with given names and labels
class CreateChosenBooleanForm(forms.Form):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('customFields')
        super(CreateChosenBooleanForm, self).__init__(*args, **kwargs)

        #create a BooleanField for each item
        for i, field in enumerate(fields):
            self.fields['custom_%s' % i] = forms.BooleanField(label=field['name'], required=False, help_text=field['description'])
            self.fields['custom_%s' % i].widget.attrs.update({
                'class': 'checkbox',
            })

    def getAllFields(self):
        for name, value in self.cleaned_data.items():
            #if name.startswith('custom_'):
            yield (name, value)


class CreateChosenBooleanFormWithoutDesc(forms.Form):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('customFields')
        super(CreateChosenBooleanFormWithoutDesc, self).__init__(*args, **kwargs)

        #create a BooleanField for each item
        for i, field in enumerate(fields):
            #subject number and study group are checked by default
            if(field['name'] == "subject_number" or field['name'] == "study_group_name"):
                self.fields[field['name'] + '_custom_%s' % i] = forms.BooleanField(label=field['name'], required=False, initial=True)
            
            #all others are unchecked by default
            else:
                self.fields[field['name'] + '_custom_%s' % i] = forms.BooleanField(label=field['name'], required=False, initial=False)


    def getAllFields(self):
        for name, value in self.cleaned_data.items():
            #if name.startswith('custom_'):
            yield (name, value)


class CreateChosenFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('customFields')
        super(CreateChosenFilterForm, self).__init__(*args, **kwargs)

    #for field in fields:
        for i, field in enumerate(fields):
            self.fields[field['name'] + '_checkbox'] = forms.BooleanField(label=field['name'], required=False)
            self.fields[field['name'] + '_checkbox'].group = field['name']
            self.fields[field['name'] + '_dropdown'] = forms.CharField(label=field['name'], widget=forms.Select(choices=Integer_Symbols), required=False)
            self.fields[field['name'] + '_dropdown'].group = field['name']
            self.fields[field['name'] + '_dropdown'].widget.attrs.update({
                'class': 'left-spacing',
            })
            self.fields[field['name'] + '_text'] = forms.CharField(label=field['name'], required=False)
            self.fields[field['name'] + '_text'].group = field['name']
            self.fields[field['name'] + '_text'].widget.attrs.update({
                'class': 'left-spacing',
            })

    def getAllFields(self):
        for name, value in self.cleaned_data.items():
            #if name.startswith('custom_'):
            yield (name, value)
