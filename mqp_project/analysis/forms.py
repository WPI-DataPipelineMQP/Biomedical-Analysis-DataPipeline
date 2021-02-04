from django import forms

# Dynamic form that uses customFields arg to create boolean fields with given names and labels
# taken from Django practice repo


class CreateChosenBooleanForm(forms.Form):
    bins = forms.IntegerField(initial=10, min_value=1)


    def __init__(self, *args, **kwargs):
        attributes = kwargs.pop('customFields')
        super(CreateChosenBooleanForm, self).__init__(*args, **kwargs)

        self.fields["radio"] = forms.ChoiceField(widget=forms.RadioSelect, choices=attributes)

    #    for i, field in enumerate(fields):
    #         self.fields['custom_%s' % i] = forms.BooleanField(
    #             label=field, required=False)
    #         self.fields['custom_%s' % i].widget.attrs.update({
    #             'class': 'checkbox',
    #         })
            #help_texts[field['name']] = '<span class="my-class">'+field['description']+'</span>'
        #print(fields)

    def getAllFields(self):
        for name, value in self.cleaned_data.items():
            # if name.startswith('custom_'):
            yield (name, value)


class CreateChosenBooleanFormNoBins(forms.Form):

    def __init__(self, *args, **kwargs):
        attributes = kwargs.pop('customFields')
        super(CreateChosenBooleanFormNoBins, self).__init__(*args, **kwargs)

        self.fields["radio"] = forms.ChoiceField(widget=forms.RadioSelect, choices=attributes)

    #    for i, field in enumerate(fields):
    #         self.fields['custom_%s' % i] = forms.BooleanField(
    #             label=field, required=False)
    #         self.fields['custom_%s' % i].widget.attrs.update({
    #             'class': 'checkbox',
    #         })
            #help_texts[field['name']] = '<span class="my-class">'+field['description']+'</span>'
        #print(fields)

    def getAllFields(self):
        for name, value in self.cleaned_data.items():
            # if name.startswith('custom_'):
            yield (name, value)
