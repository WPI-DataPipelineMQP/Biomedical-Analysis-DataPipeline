from django import forms

# Dynamic form that uses customFields arg to create boolean fields with given names and labels


class CreateChosenBooleanForm(forms.Form):
    #field for the number of bins
    bins = forms.IntegerField(initial=10, min_value=1)

    def __init__(self, *args, **kwargs):
        attributes = kwargs.pop('customFields')
        super(CreateChosenBooleanForm, self).__init__(*args, **kwargs)

        #here, we put all attributes as choices in the same field
        self.fields["radio"] = forms.ChoiceField(widget=forms.RadioSelect, choices=attributes)

    #retrieves all fields in the form and their values one by one
    def getAllFields(self):
        for name, value in self.cleaned_data.items():
            yield (name, value)


class CreateChosenBooleanFormScatter(forms.Form):

    def __init__(self, *args, **kwargs):
        attributes = kwargs.pop('customFields')
        super(CreateChosenBooleanFormScatter, self).__init__(*args, **kwargs)

        #we need two of the same question, so they are in the form as two different fields
        self.fields["x_radio"] = forms.ChoiceField(widget=forms.RadioSelect,choices=attributes,label="X-Axis")
        self.fields["y_radio"] = forms.ChoiceField(widget=forms.RadioSelect,choices=attributes,label="Y-Axis")

    def getAllFields(self):
        for name, value in self.cleaned_data.items():
            yield (name, value)
