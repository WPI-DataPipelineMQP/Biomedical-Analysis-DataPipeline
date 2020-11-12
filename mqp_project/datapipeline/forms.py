from django import forms

Integer_Symbols = [
    ('equal', '='),
    ('notequal', '!='),
    ('less', '<'),
    ('greater', '>'),
    ('lessorequal', '<='),
    ('greaterorequal', '>='),
]
NonInteger_Symbols = [
    ('equal', '='),
    ('notequal', '!='),
]

# Dynamic form that uses customFields arg to create boolean fields with given names and labels
#taken from Django practice repo
class CreateChosenBooleanForm(forms.Form):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('customFields')
        super(CreateChosenBooleanForm, self).__init__(*args, **kwargs)

        for field in fields:
            self.fields[field['id']] = forms.BooleanField(label=field['name'], required=False)

class CreateChosenFilterForm(forms.Form):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('customFields')
        super(CreateChosenBooleanForm, self).__init__(*args, **kwargs)

    #for field in fields:
        


class CreateHeartRateForm(forms.Form):
    viewHRDateTime = forms.BooleanField(label= 'HeartRate.date_time', required = False)
    viewHRHeartRate = forms.BooleanField(label= 'HeartRate.heart_rate', required = False)
    viewSubjectNumber = forms.BooleanField(label= 'subject_number', required = False) #required = True ?
    viewSGName = forms.BooleanField(label= 'study_group_name', required = False) #required = True ?

    filterHRDateTime = forms.BooleanField(label= 'HeartRate.date_time', required = False)
    filterHRHeartRate = forms.BooleanField(label= 'HeartRate.heart_rate', required = False)
    filterSubjectNumber = forms.BooleanField(label= 'subject_number', required = False)
    filterSGName = forms.BooleanField(label= 'study_group_name', required = False)

    filterSymHRDateTime = forms.CharField(label='HeartRate.date_time', widget=forms.Select(choices=Integer_Symbols))
    filterSymHRHeartRate = forms.CharField(label='HeartRate.heart_rate', widget=forms.Select(choices=Integer_Symbols))
    filterSymSubjectNumber = forms.CharField(label='subject_number', widget=forms.Select(choices=NonInteger_Symbols))
    filterSymSGName = forms.CharField(label='study_group_name', widget=forms.Select(choices=NonInteger_Symbols))

    filterValueHRDateTime = forms.CharField(label='HeartRate.date_time', required = False)
    filterValueHRHeartRate = forms.CharField(label='HeartRate.heart_rate', required = False)
    filterValueSubjectNumber = forms.CharField(label='subject_number', required = False)
    filterValueSGName = forms.CharField(label='study_group_name', required = False)

class CreateCorsiForm(forms.Form):
    viewCBinaryResult = forms.BooleanField(label= 'Corsi.binary_result', required = False)
    viewCHighestSpan = forms.BooleanField(label= 'Corsi.highest_corsi_span', required = False)
    viewCNumOfItems = forms.BooleanField(label= 'Corsi.num_of_items', required = False)
    viewCSeqNum = forms.BooleanField(label= 'Corsi.sequence_number', required = False)
    viewCTrial = forms.BooleanField(label= 'Corsi.trial', required = False)
    viewSubjectNumber = forms.BooleanField(label= 'subject_number', required = False) #required = True ?
    viewSGName = forms.BooleanField(label= 'study_group_name', required = False) #required = True ?

    filterCBinaryResult = forms.BooleanField(label= 'Corsi.binary_result', required = False)
    filterCHighestSpan = forms.BooleanField(label= 'Corsi.highest_corsi_span', required = False)
    filterCNumOfItems = forms.BooleanField(label= 'Corsi.num_of_items', required = False)
    filterCSeqNum = forms.BooleanField(label= 'Corsi.sequence_number', required = False)
    filterCTrial = forms.BooleanField(label= 'Corsi.trial', required = False)
    filterSubjectNumber = forms.BooleanField(label= 'subject_number', required = False)
    filterSGName = forms.BooleanField(label= 'study_group_name', required = False)

    filterSymCBianaryResult = forms.CharField(label='Corsi.binary_result', widget=forms.Select(choices=Integer_Symbols))
    filterSymCHighestSpan = forms.CharField(label='Corsi.highest_corsi_span', widget=forms.Select(choices=Integer_Symbols))
    filterSymCNumOfItems = forms.CharField(label='Corsi.num_of_items', widget=forms.Select(choices=Integer_Symbols))
    filterSymCSeqNum = forms.CharField(label='Corsi.sequence_number', widget=forms.Select(choices=Integer_Symbols))
    filterSymCTrial = forms.CharField(label='Corsi.trial', widget=forms.Select(choices=Integer_Symbols))
    filterSymSubjectNumber = forms.CharField(label='subject_number', widget=forms.Select(choices=NonInteger_Symbols))
    filterSymSGName = forms.CharField(label='study_group_name', widget=forms.Select(choices=NonInteger_Symbols))

class CreateFlankerForm(forms.Form):
    viewFResponseTime = forms.BooleanField(label= 'Flanker.response_time', required = False)
    viewFIsCongruent = forms.BooleanField(label= 'Flanker.is_congruent', required = False)
    viewFResult = forms.BooleanField(label= 'Flanker.result', required = False)
    viewFTrial = forms.BooleanField(label= 'Flanker.trial', required = False)
    viewSubjectNumber = forms.BooleanField(label= 'subject_number', required = False) #required = True ?
    viewSGName = forms.BooleanField(label= 'study_group_name', required = False) #required = True ?

    filterFResponseTime = forms.BooleanField(label= 'Flanker.response_time', required = False)
    filterFIsCongruent = forms.BooleanField(label= 'Flanker.is_congruent', required = False)
    filterFResult = forms.BooleanField(label= 'Flanker.result', required = False)
    filterFTrial = forms.BooleanField(label= 'Flanker.trial', required = False)
    filterSubjectNumber = forms.BooleanField(label= 'subject_number', required = False)
    filterSGName = forms.BooleanField(label= 'study_group_name', required = False)

    filterSymFResponseTime = forms.CharField(label='Flanker.response_time', widget=forms.Select(choices=Integer_Symbols))
    filterSymFIsCongruent = forms.CharField(label='Flanker.is_congruent', widget=forms.Select(choices=Integer_Symbols))
    filterSymFResult = forms.CharField(label='Flanker.result', widget=forms.Select(choices=Integer_Symbols))
    filterSymFTrial = forms.CharField(label='Flanker.trial', widget=forms.Select(choices=Integer_Symbols))
    filterSymSubjectNumber = forms.CharField(label='subject_number', widget=forms.Select(choices=NonInteger_Symbols))
    filterSymSGName = forms.CharField(label='study_group_name', widget=forms.Select(choices=NonInteger_Symbols))



class CreateHeartRateANDCorsi(forms.Form):
    viewHRDateTime = forms.BooleanField(label= 'HeartRate.date_time', required = False)
    viewHRHeartRate = forms.BooleanField(label= 'HeartRate.heart_rate', required = False)
    filterHRDateTime = forms.BooleanField(label= 'HeartRate.date_time', required = False)
    filterHRHeartRate = forms.BooleanField(label= 'HeartRate.heart_rate', required = False)
    filterSymHRDateTime = forms.CharField(label='HeartRate.date_time', widget=forms.Select(choices=Integer_Symbols))
    filterSymHRHeartRate = forms.CharField(label='HeartRate.heart_rate', widget=forms.Select(choices=Integer_Symbols))

    viewCBinaryResult = forms.BooleanField(label= 'Corsi.binary_result', required = False)
    viewCHighestSpan = forms.BooleanField(label= 'Corsi.highest_corsi_span', required = False)
    viewCNumOfItems = forms.BooleanField(label= 'Corsi.num_of_items', required = False)
    viewCSeqNum = forms.BooleanField(label= 'Corsi.sequence_number', required = False)
    viewCTrial = forms.BooleanField(label= 'Corsi.trial', required = False)
    filterCBinaryResult = forms.BooleanField(label='Corsi.binary_result', required=False)
    filterCHighestSpan = forms.BooleanField(label='Corsi.highest_corsi_span', required=False)
    filterCNumOfItems = forms.BooleanField(label='Corsi.num_of_items', required=False)
    filterCSeqNum = forms.BooleanField(label='Corsi.sequence_number', required=False)
    filterCTrial = forms.BooleanField(label='Corsi.trial', required=False)
    filterSymCBianaryResult = forms.CharField(label='Corsi.binary_result', widget=forms.Select(choices=Integer_Symbols))
    filterSymCHighestSpan = forms.CharField(label='Corsi.highest_corsi_span', widget=forms.Select(choices=Integer_Symbols))
    filterSymCNumOfItems = forms.CharField(label='Corsi.num_of_items', widget=forms.Select(choices=Integer_Symbols))
    filterSymCSeqNum = forms.CharField(label='Corsi.sequence_number', widget=forms.Select(choices=Integer_Symbols))
    filterSymCTrial = forms.CharField(label='Corsi.trial', widget=forms.Select(choices=Integer_Symbols))

    viewSubjectNumber = forms.BooleanField(label= 'subject_number', required = False) #required = True ?
    viewSGName = forms.BooleanField(label= 'study_group_name', required = False) #required = True ?
    filterSubjectNumber = forms.BooleanField(label= 'subject_number', required = False)
    filterSGName = forms.BooleanField(label= 'study_group_name', required = False)
    filterSymSubjectNumber = forms.CharField(label='subject_number', widget=forms.Select(choices=NonInteger_Symbols))
    filterSymSGName = forms.CharField(label='study_group_name', widget=forms.Select(choices=NonInteger_Symbols))



class CreateHeartRateANDFlanker(forms.Form):
    viewHRDateTime = forms.BooleanField(label= 'HeartRate.date_time', required = False)
    viewHRHeartRate = forms.BooleanField(label= 'HeartRate.heart_rate', required = False)
    filterHRDateTime = forms.BooleanField(label= 'HeartRate.date_time', required = False)
    filterHRHeartRate = forms.BooleanField(label= 'HeartRate.heart_rate', required = False)
    filterSymHRDateTime = forms.CharField(label='HeartRate.date_time', widget=forms.Select(choices=Integer_Symbols))
    filterSymHRHeartRate = forms.CharField(label='HeartRate.heart_rate', widget=forms.Select(choices=Integer_Symbols))

    viewFResponseTime = forms.BooleanField(label= 'Flanker.response_time', required = False)
    viewFIsCongruent = forms.BooleanField(label= 'Flanker.is_congruent', required = False)
    viewFResult = forms.BooleanField(label= 'Flanker.result', required = False)
    viewFTrial = forms.BooleanField(label= 'Flanker.trial', required = False)
    filterFResponseTime = forms.BooleanField(label='Flanker.response_time', required=False)
    filterFIsCongruent = forms.BooleanField(label='Flanker.is_congruent', required=False)
    filterFResult = forms.BooleanField(label='Flanker.result', required=False)
    filterFTrial = forms.BooleanField(label='Flanker.trial', required=False)
    filterSymFResponseTime = forms.CharField(label='Flanker.response_time', widget=forms.Select(choices=Integer_Symbols))
    filterSymFIsCongruent = forms.CharField(label='Flanker.is_congruent', widget=forms.Select(choices=Integer_Symbols))
    filterSymFResult = forms.CharField(label='Flanker.result', widget=forms.Select(choices=Integer_Symbols))
    filterSymFTrial = forms.CharField(label='Flanker.trial', widget=forms.Select(choices=Integer_Symbols))

    viewSubjectNumber = forms.BooleanField(label= 'subject_number', required = False) #required = True ?
    viewSGName = forms.BooleanField(label= 'study_group_name', required = False) #required = True ?
    filterSubjectNumber = forms.BooleanField(label='subject_number', required=False)
    filterSGName = forms.BooleanField(label='study_group_name', required=False)
    filterSymSubjectNumber = forms.CharField(label='subject_number', widget=forms.Select(choices=NonInteger_Symbols))
    filterSymSGName = forms.CharField(label='study_group_name', widget=forms.Select(choices=NonInteger_Symbols))

class CreateCorsiANDFlanker(forms.Form):
    viewCBinaryResult = forms.BooleanField(label= 'Corsi.binary_result', required = False)
    viewCHighestSpan = forms.BooleanField(label= 'Corsi.highest_corsi_span', required = False)
    viewCNumOfItems = forms.BooleanField(label= 'Corsi.num_of_items', required = False)
    viewCSeqNum = forms.BooleanField(label= 'Corsi.sequence_number', required = False)
    viewCTrial = forms.BooleanField(label= 'Corsi.trial', required = False)
    filterCBinaryResult = forms.BooleanField(label='Corsi.binary_result', required=False)
    filterCHighestSpan = forms.BooleanField(label='Corsi.highest_corsi_span', required=False)
    filterCNumOfItems = forms.BooleanField(label='Corsi.num_of_items', required=False)
    filterCSeqNum = forms.BooleanField(label='Corsi.sequence_number', required=False)
    filterCTrial = forms.BooleanField(label='Corsi.trial', required=False)
    filterSymCBianaryResult = forms.CharField(label='Corsi.binary_result', widget=forms.Select(choices=Integer_Symbols))
    filterSymCHighestSpan = forms.CharField(label='Corsi.highest_corsi_span', widget=forms.Select(choices=Integer_Symbols))
    filterSymCNumOfItems = forms.CharField(label='Corsi.num_of_items', widget=forms.Select(choices=Integer_Symbols))
    filterSymCSeqNum = forms.CharField(label='Corsi.sequence_number', widget=forms.Select(choices=Integer_Symbols))
    filterSymCTrial = forms.CharField(label='Corsi.trial', widget=forms.Select(choices=Integer_Symbols))

    viewFResponseTime = forms.BooleanField(label= 'Flanker.response_time', required = False)
    viewFIsCongruent = forms.BooleanField(label= 'Flanker.is_congruent', required = False)
    viewFResult = forms.BooleanField(label= 'Flanker.result', required = False)
    viewFTrial = forms.BooleanField(label= 'Flanker.trial', required = False)
    filterFResponseTime = forms.BooleanField(label='Flanker.response_time', required=False)
    filterFIsCongruent = forms.BooleanField(label='Flanker.is_congruent', required=False)
    filterFResult = forms.BooleanField(label='Flanker.result', required=False)
    filterFTrial = forms.BooleanField(label='Flanker.trial', required=False)
    filterSymFResponseTime = forms.CharField(label='Flanker.response_time', widget=forms.Select(choices=Integer_Symbols))
    filterSymFIsCongruent = forms.CharField(label='Flanker.is_congruent', widget=forms.Select(choices=Integer_Symbols))
    filterSymFResult = forms.CharField(label='Flanker.result', widget=forms.Select(choices=Integer_Symbols))
    filterSymFTrial = forms.CharField(label='Flanker.trial', widget=forms.Select(choices=Integer_Symbols))

    viewSubjectNumber = forms.BooleanField(label= 'subject_number', required = False) #required = True ?
    viewSGName = forms.BooleanField(label= 'study_group_name', required = False) #required = True ?
    filterSubjectNumber = forms.BooleanField(label='subject_number', required=False)
    filterSGName = forms.BooleanField(label='study_group_name', required=False)
    filterSymSubjectNumber = forms.CharField(label='subject_number', widget=forms.Select(choices=NonInteger_Symbols))
    filterSymSGName = forms.CharField(label='study_group_name', widget=forms.Select(choices=NonInteger_Symbols))

class CreateALL(forms.Form):
    viewHRDateTime = forms.BooleanField(label= 'HeartRate.date_time', required = False)
    viewHRHeartRate = forms.BooleanField(label= 'HeartRate.heart_rate', required = False)
    filterHRDateTime = forms.BooleanField(label= 'HeartRate.date_time', required = False)
    filterHRHeartRate = forms.BooleanField(label= 'HeartRate.heart_rate', required = False)
    filterSymHRDateTime = forms.CharField(label='HeartRate.date_time', widget=forms.Select(choices=Integer_Symbols))
    filterSymHRHeartRate = forms.CharField(label='HeartRate.heart_rate', widget=forms.Select(choices=Integer_Symbols))

    viewCBinaryResult = forms.BooleanField(label= 'Corsi.binary_result', required = False)
    viewCHighestSpan = forms.BooleanField(label= 'Corsi.highest_corsi_span', required = False)
    viewCNumOfItems = forms.BooleanField(label= 'Corsi.num_of_items', required = False)
    viewCSeqNum = forms.BooleanField(label= 'Corsi.sequence_number', required = False)
    viewCTrial = forms.BooleanField(label= 'Corsi.trial', required = False)
    filterCBinaryResult = forms.BooleanField(label='Corsi.binary_result', required=False)
    filterCHighestSpan = forms.BooleanField(label='Corsi.highest_corsi_span', required=False)
    filterCNumOfItems = forms.BooleanField(label='Corsi.num_of_items', required=False)
    filterCSeqNum = forms.BooleanField(label='Corsi.sequence_number', required=False)
    filterCTrial = forms.BooleanField(label='Corsi.trial', required=False)
    filterSymCBianaryResult = forms.CharField(label='Corsi.binary_result', widget=forms.Select(choices=Integer_Symbols))
    filterSymCHighestSpan = forms.CharField(label='Corsi.highest_corsi_span', widget=forms.Select(choices=Integer_Symbols))
    filterSymCNumOfItems = forms.CharField(label='Corsi.num_of_items', widget=forms.Select(choices=Integer_Symbols))
    filterSymCSeqNum = forms.CharField(label='Corsi.sequence_number', widget=forms.Select(choices=Integer_Symbols))
    filterSymCTrial = forms.CharField(label='Corsi.trial', widget=forms.Select(choices=Integer_Symbols))

    viewFResponseTime = forms.BooleanField(label= 'Flanker.response_time', required = False)
    viewFIsCongruent = forms.BooleanField(label= 'Flanker.is_congruent', required = False)
    viewFResult = forms.BooleanField(label= 'Flanker.result', required = False)
    viewFTrial = forms.BooleanField(label= 'Flanker.trial', required = False)
    filterFResponseTime = forms.BooleanField(label='Flanker.response_time', required=False)
    filterFIsCongruent = forms.BooleanField(label='Flanker.is_congruent', required=False)
    filterFResult = forms.BooleanField(label='Flanker.result', required=False)
    filterFTrial = forms.BooleanField(label='Flanker.trial', required=False)
    filterSymFResponseTime = forms.CharField(label='Flanker.response_time', widget=forms.Select(choices=Integer_Symbols))
    filterSymFIsCongruent = forms.CharField(label='Flanker.is_congruent', widget=forms.Select(choices=Integer_Symbols))
    filterSymFResult = forms.CharField(label='Flanker.result', widget=forms.Select(choices=Integer_Symbols))
    filterSymFTrial = forms.CharField(label='Flanker.trial', widget=forms.Select(choices=Integer_Symbols))

    viewSubjectNumber = forms.BooleanField(label= 'subject_number', required = False) #required = True ?
    viewSGName = forms.BooleanField(label= 'study_group_name', required = False) #required = True ?
    filterSubjectNumber = forms.BooleanField(label='subject_number', required=False)
    filterSGName = forms.BooleanField(label='study_group_name', required=False)
    filterSymSubjectNumber = forms.CharField(label='subject_number', widget=forms.Select(choices=NonInteger_Symbols))
    filterSymSGName = forms.CharField(label='study_group_name', widget=forms.Select(choices=NonInteger_Symbols))

# class CreateHeartRateForm(forms.Form):
#     viewHRDateTime = forms.NullBooleanField(label= 'HeartRate.date_time', required = False)
#     viewHRHeartRate = forms.NullBooleanField(label= 'HeartRate.heart_rate', required = False)
#     viewSubjectNumber = forms.NullBooleanField(label= 'subject_number', required = False) #required = True ?
#     viewSGName = forms.NullBooleanField(label= 'study_group_name', required = False) #required = True ?
#
#     filterHRDateTime = forms.NullBooleanField(label= 'HeartRate.date_time', required = False)
#     filterHRHeartRate = forms.NullBooleanField(label= 'HeartRate.heart_rate', required = False)
#     filterSubjectNumber = forms.NullBooleanField(label= 'subject_number', required = False)
#     filterSGName = forms.NullBooleanField(label= 'study_group_name', required = False)
#
#     filterSymHRDateTime = forms.CharField(label='HeartRate.date_time', widget=forms.Select(choices=Integer_Symbols))
#     filterSymHRHeartRate = forms.CharField(label='HeartRate.heart_rate', widget=forms.Select(choices=Integer_Symbols))
#     filterSymSubjectNumber = forms.CharField(label='subject_number', widget=forms.Select(choices=NonInteger_Symbols))
#     filterSymSGName = forms.CharField(label='study_group_name', widget=forms.Select(choices=NonInteger_Symbols))
#
#     filterValueHRDateTime = forms.CharField(label='HeartRate.date_time', required = False)
#     filterValueHRHeartRate = forms.CharField(label='HeartRate.heart_rate', required = False)
#     filterValueSubjectNumber = forms.CharField(label='subject_number', required = False)
#     filterValueSGName = forms.CharField(label='study_group_name', required = False)
#
# class CreateCorsiForm(forms.Form):
#     viewCBinaryResult = forms.NullBooleanField(label= 'Corsi.binary_result', required = False)
#     viewCHighestSpan = forms.NullBooleanField(label= 'Corsi.highest_corsi_span', required = False)
#     viewCNumOfItems = forms.NullBooleanField(label= 'Corsi.num_of_items', required = False)
#     viewCSeqNum = forms.NullBooleanField(label= 'Corsi.sequence_number', required = False)
#     viewCTrial = forms.NullBooleanField(label= 'Corsi.trial', required = False)
#     viewSubjectNumber = forms.NullBooleanField(label= 'subject_number', required = False) #required = True ?
#     viewSGName = forms.NullBooleanField(label= 'study_group_name', required = False) #required = True ?
#
#     filterCBinaryResult = forms.NullBooleanField(label= 'Corsi.binary_result', required = False)
#     filterCHighestSpan = forms.NullBooleanField(label= 'Corsi.highest_corsi_span', required = False)
#     filterCNumOfItems = forms.NullBooleanField(label= 'Corsi.num_of_items', required = False)
#     filterCSeqNum = forms.NullBooleanField(label= 'Corsi.sequence_number', required = False)
#     filterCTrial = forms.NullBooleanField(label= 'Corsi.trial', required = False)
#     filterSubjectNumber = forms.NullBooleanField(label= 'subject_number', required = False)
#     filterSGName = forms.NullBooleanField(label= 'study_group_name', required = False)
#
#     filterSymCBianaryResult = forms.CharField(label='Corsi.binary_result', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCHighestSpan = forms.CharField(label='Corsi.highest_corsi_span', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCNumOfItems = forms.CharField(label='Corsi.num_of_items', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCSeqNum = forms.CharField(label='Corsi.sequence_number', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCTrial = forms.CharField(label='Corsi.trial', widget=forms.Select(choices=Integer_Symbols))
#     filterSymSubjectNumber = forms.CharField(label='subject_number', widget=forms.Select(choices=NonInteger_Symbols))
#     filterSymSGName = forms.CharField(label='study_group_name', widget=forms.Select(choices=NonInteger_Symbols))
#
# class CreateFlankerForm(forms.Form):
#     viewFResponseTime = forms.NullBooleanField(label= 'Flanker.response_time', required = False)
#     viewFIsCongruent = forms.NullBooleanField(label= 'Flanker.is_congruent', required = False)
#     viewFResult = forms.NullBooleanField(label= 'Flanker.result', required = False)
#     viewFTrial = forms.NullBooleanField(label= 'Flanker.trial', required = False)
#     viewSubjectNumber = forms.NullBooleanField(label= 'subject_number', required = False) #required = True ?
#     viewSGName = forms.NullBooleanField(label= 'study_group_name', required = False) #required = True ?
#
#     filterFResponseTime = forms.NullBooleanField(label= 'Flanker.response_time', required = False)
#     filterFIsCongruent = forms.NullBooleanField(label= 'Flanker.is_congruent', required = False)
#     filterFResult = forms.NullBooleanField(label= 'Flanker.result', required = False)
#     filterFTrial = forms.NullBooleanField(label= 'Flanker.trial', required = False)
#     filterSubjectNumber = forms.NullBooleanField(label= 'subject_number', required = False)
#     filterSGName = forms.NullBooleanField(label= 'study_group_name', required = False)
#
#     filterSymFResponseTime = forms.CharField(label='Flanker.response_time', widget=forms.Select(choices=Integer_Symbols))
#     filterSymFIsCongruent = forms.CharField(label='Flanker.is_congruent', widget=forms.Select(choices=Integer_Symbols))
#     filterSymFResult = forms.CharField(label='Flanker.result', widget=forms.Select(choices=Integer_Symbols))
#     filterSymFTrial = forms.CharField(label='Flanker.trial', widget=forms.Select(choices=Integer_Symbols))
#     filterSymSubjectNumber = forms.CharField(label='subject_number', widget=forms.Select(choices=NonInteger_Symbols))
#     filterSymSGName = forms.CharField(label='study_group_name', widget=forms.Select(choices=NonInteger_Symbols))
#
#
#
# class CreateHeartRateANDCorsi(forms.Form):
#     viewHRDateTime = forms.NullBooleanField(label= 'HeartRate.date_time', required = False)
#     viewHRHeartRate = forms.NullBooleanField(label= 'HeartRate.heart_rate', required = False)
#     filterHRDateTime = forms.NullBooleanField(label= 'HeartRate.date_time', required = False)
#     filterHRHeartRate = forms.NullBooleanField(label= 'HeartRate.heart_rate', required = False)
#     filterSymHRDateTime = forms.CharField(label='HeartRate.date_time', widget=forms.Select(choices=Integer_Symbols))
#     filterSymHRHeartRate = forms.CharField(label='HeartRate.heart_rate', widget=forms.Select(choices=Integer_Symbols))
#
#     viewCBinaryResult = forms.NullBooleanField(label= 'Corsi.binary_result', required = False)
#     viewCHighestSpan = forms.NullBooleanField(label= 'Corsi.highest_corsi_span', required = False)
#     viewCNumOfItems = forms.NullBooleanField(label= 'Corsi.num_of_items', required = False)
#     viewCSeqNum = forms.NullBooleanField(label= 'Corsi.sequence_number', required = False)
#     viewCTrial = forms.NullBooleanField(label= 'Corsi.trial', required = False)
#     filterCBinaryResult = forms.NullBooleanField(label='Corsi.binary_result', required=False)
#     filterCHighestSpan = forms.NullBooleanField(label='Corsi.highest_corsi_span', required=False)
#     filterCNumOfItems = forms.NullBooleanField(label='Corsi.num_of_items', required=False)
#     filterCSeqNum = forms.NullBooleanField(label='Corsi.sequence_number', required=False)
#     filterCTrial = forms.NullBooleanField(label='Corsi.trial', required=False)
#     filterSymCBianaryResult = forms.CharField(label='Corsi.binary_result', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCHighestSpan = forms.CharField(label='Corsi.highest_corsi_span', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCNumOfItems = forms.CharField(label='Corsi.num_of_items', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCSeqNum = forms.CharField(label='Corsi.sequence_number', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCTrial = forms.CharField(label='Corsi.trial', widget=forms.Select(choices=Integer_Symbols))
#
#     viewSubjectNumber = forms.NullBooleanField(label= 'subject_number', required = False) #required = True ?
#     viewSGName = forms.NullBooleanField(label= 'study_group_name', required = False) #required = True ?
#     filterSubjectNumber = forms.NullBooleanField(label= 'subject_number', required = False)
#     filterSGName = forms.NullBooleanField(label= 'study_group_name', required = False)
#     filterSymSubjectNumber = forms.CharField(label='subject_number', widget=forms.Select(choices=NonInteger_Symbols))
#     filterSymSGName = forms.CharField(label='study_group_name', widget=forms.Select(choices=NonInteger_Symbols))
#
#
#
# class CreateHeartRateANDFlanker(forms.Form):
#     viewHRDateTime = forms.NullBooleanField(label= 'HeartRate.date_time', required = False)
#     viewHRHeartRate = forms.NullBooleanField(label= 'HeartRate.heart_rate', required = False)
#     filterHRDateTime = forms.NullBooleanField(label= 'HeartRate.date_time', required = False)
#     filterHRHeartRate = forms.NullBooleanField(label= 'HeartRate.heart_rate', required = False)
#     filterSymHRDateTime = forms.CharField(label='HeartRate.date_time', widget=forms.Select(choices=Integer_Symbols))
#     filterSymHRHeartRate = forms.CharField(label='HeartRate.heart_rate', widget=forms.Select(choices=Integer_Symbols))
#
#     viewFResponseTime = forms.NullBooleanField(label= 'Flanker.response_time', required = False)
#     viewFIsCongruent = forms.NullBooleanField(label= 'Flanker.is_congruent', required = False)
#     viewFResult = forms.NullBooleanField(label= 'Flanker.result', required = False)
#     viewFTrial = forms.NullBooleanField(label= 'Flanker.trial', required = False)
#     filterFResponseTime = forms.NullBooleanField(label='Flanker.response_time', required=False)
#     filterFIsCongruent = forms.NullBooleanField(label='Flanker.is_congruent', required=False)
#     filterFResult = forms.NullBooleanField(label='Flanker.result', required=False)
#     filterFTrial = forms.NullBooleanField(label='Flanker.trial', required=False)
#     filterSymFResponseTime = forms.CharField(label='Flanker.response_time', widget=forms.Select(choices=Integer_Symbols))
#     filterSymFIsCongruent = forms.CharField(label='Flanker.is_congruent', widget=forms.Select(choices=Integer_Symbols))
#     filterSymFResult = forms.CharField(label='Flanker.result', widget=forms.Select(choices=Integer_Symbols))
#     filterSymFTrial = forms.CharField(label='Flanker.trial', widget=forms.Select(choices=Integer_Symbols))
#
#     viewSubjectNumber = forms.NullBooleanField(label= 'subject_number', required = False) #required = True ?
#     viewSGName = forms.NullBooleanField(label= 'study_group_name', required = False) #required = True ?
#     filterSubjectNumber = forms.NullBooleanField(label='subject_number', required=False)
#     filterSGName = forms.NullBooleanField(label='study_group_name', required=False)
#     filterSymSubjectNumber = forms.CharField(label='subject_number', widget=forms.Select(choices=NonInteger_Symbols))
#     filterSymSGName = forms.CharField(label='study_group_name', widget=forms.Select(choices=NonInteger_Symbols))
#
# class CreateCorsiANDFlanker(forms.Form):
#     viewCBinaryResult = forms.NullBooleanField(label= 'Corsi.binary_result', required = False)
#     viewCHighestSpan = forms.NullBooleanField(label= 'Corsi.highest_corsi_span', required = False)
#     viewCNumOfItems = forms.NullBooleanField(label= 'Corsi.num_of_items', required = False)
#     viewCSeqNum = forms.NullBooleanField(label= 'Corsi.sequence_number', required = False)
#     viewCTrial = forms.NullBooleanField(label= 'Corsi.trial', required = False)
#     filterCBinaryResult = forms.NullBooleanField(label='Corsi.binary_result', required=False)
#     filterCHighestSpan = forms.NullBooleanField(label='Corsi.highest_corsi_span', required=False)
#     filterCNumOfItems = forms.NullBooleanField(label='Corsi.num_of_items', required=False)
#     filterCSeqNum = forms.NullBooleanField(label='Corsi.sequence_number', required=False)
#     filterCTrial = forms.NullBooleanField(label='Corsi.trial', required=False)
#     filterSymCBianaryResult = forms.CharField(label='Corsi.binary_result', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCHighestSpan = forms.CharField(label='Corsi.highest_corsi_span', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCNumOfItems = forms.CharField(label='Corsi.num_of_items', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCSeqNum = forms.CharField(label='Corsi.sequence_number', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCTrial = forms.CharField(label='Corsi.trial', widget=forms.Select(choices=Integer_Symbols))
#
#     viewFResponseTime = forms.NullBooleanField(label= 'Flanker.response_time', required = False)
#     viewFIsCongruent = forms.NullBooleanField(label= 'Flanker.is_congruent', required = False)
#     viewFResult = forms.NullBooleanField(label= 'Flanker.result', required = False)
#     viewFTrial = forms.NullBooleanField(label= 'Flanker.trial', required = False)
#     filterFResponseTime = forms.NullBooleanField(label='Flanker.response_time', required=False)
#     filterFIsCongruent = forms.NullBooleanField(label='Flanker.is_congruent', required=False)
#     filterFResult = forms.NullBooleanField(label='Flanker.result', required=False)
#     filterFTrial = forms.NullBooleanField(label='Flanker.trial', required=False)
#     filterSymFResponseTime = forms.CharField(label='Flanker.response_time', widget=forms.Select(choices=Integer_Symbols))
#     filterSymFIsCongruent = forms.CharField(label='Flanker.is_congruent', widget=forms.Select(choices=Integer_Symbols))
#     filterSymFResult = forms.CharField(label='Flanker.result', widget=forms.Select(choices=Integer_Symbols))
#     filterSymFTrial = forms.CharField(label='Flanker.trial', widget=forms.Select(choices=Integer_Symbols))
#
#     viewSubjectNumber = forms.NullBooleanField(label= 'subject_number', required = False) #required = True ?
#     viewSGName = forms.NullBooleanField(label= 'study_group_name', required = False) #required = True ?
#     filterSubjectNumber = forms.NullBooleanField(label='subject_number', required=False)
#     filterSGName = forms.NullBooleanField(label='study_group_name', required=False)
#     filterSymSubjectNumber = forms.CharField(label='subject_number', widget=forms.Select(choices=NonInteger_Symbols))
#     filterSymSGName = forms.CharField(label='study_group_name', widget=forms.Select(choices=NonInteger_Symbols))
#
# class CreateALL(forms.Form):
#     viewHRDateTime = forms.NullBooleanField(label= 'HeartRate.date_time', required = False)
#     viewHRHeartRate = forms.NullBooleanField(label= 'HeartRate.heart_rate', required = False)
#     filterHRDateTime = forms.NullBooleanField(label= 'HeartRate.date_time', required = False)
#     filterHRHeartRate = forms.NullBooleanField(label= 'HeartRate.heart_rate', required = False)
#     filterSymHRDateTime = forms.CharField(label='HeartRate.date_time', widget=forms.Select(choices=Integer_Symbols))
#     filterSymHRHeartRate = forms.CharField(label='HeartRate.heart_rate', widget=forms.Select(choices=Integer_Symbols))
#
#     viewCBinaryResult = forms.NullBooleanField(label= 'Corsi.binary_result', required = False)
#     viewCHighestSpan = forms.NullBooleanField(label= 'Corsi.highest_corsi_span', required = False)
#     viewCNumOfItems = forms.NullBooleanField(label= 'Corsi.num_of_items', required = False)
#     viewCSeqNum = forms.NullBooleanField(label= 'Corsi.sequence_number', required = False)
#     viewCTrial = forms.NullBooleanField(label= 'Corsi.trial', required = False)
#     filterCBinaryResult = forms.NullBooleanField(label='Corsi.binary_result', required=False)
#     filterCHighestSpan = forms.NullBooleanField(label='Corsi.highest_corsi_span', required=False)
#     filterCNumOfItems = forms.NullBooleanField(label='Corsi.num_of_items', required=False)
#     filterCSeqNum = forms.NullBooleanField(label='Corsi.sequence_number', required=False)
#     filterCTrial = forms.NullBooleanField(label='Corsi.trial', required=False)
#     filterSymCBianaryResult = forms.CharField(label='Corsi.binary_result', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCHighestSpan = forms.CharField(label='Corsi.highest_corsi_span', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCNumOfItems = forms.CharField(label='Corsi.num_of_items', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCSeqNum = forms.CharField(label='Corsi.sequence_number', widget=forms.Select(choices=Integer_Symbols))
#     filterSymCTrial = forms.CharField(label='Corsi.trial', widget=forms.Select(choices=Integer_Symbols))
#
#     viewFResponseTime = forms.NullBooleanField(label= 'Flanker.response_time', required = False)
#     viewFIsCongruent = forms.NullBooleanField(label= 'Flanker.is_congruent', required = False)
#     viewFResult = forms.NullBooleanField(label= 'Flanker.result', required = False)
#     viewFTrial = forms.NullBooleanField(label= 'Flanker.trial', required = False)
#     filterFResponseTime = forms.NullBooleanField(label='Flanker.response_time', required=False)
#     filterFIsCongruent = forms.NullBooleanField(label='Flanker.is_congruent', required=False)
#     filterFResult = forms.NullBooleanField(label='Flanker.result', required=False)
#     filterFTrial = forms.NullBooleanField(label='Flanker.trial', required=False)
#     filterSymFResponseTime = forms.CharField(label='Flanker.response_time', widget=forms.Select(choices=Integer_Symbols))
#     filterSymFIsCongruent = forms.CharField(label='Flanker.is_congruent', widget=forms.Select(choices=Integer_Symbols))
#     filterSymFResult = forms.CharField(label='Flanker.result', widget=forms.Select(choices=Integer_Symbols))
#     filterSymFTrial = forms.CharField(label='Flanker.trial', widget=forms.Select(choices=Integer_Symbols))
#
#     viewSubjectNumber = forms.NullBooleanField(label= 'subject_number', required = False) #required = True ?
#     viewSGName = forms.NullBooleanField(label= 'study_group_name', required = False) #required = True ?
#     filterSubjectNumber = forms.NullBooleanField(label='subject_number', required=False)
#     filterSGName = forms.NullBooleanField(label='study_group_name', required=False)
#     filterSymSubjectNumber = forms.CharField(label='subject_number', widget=forms.Select(choices=NonInteger_Symbols))
#     filterSymSGName = forms.CharField(label='study_group_name', widget=forms.Select(choices=NonInteger_Symbols))

# 1	HeartRate_1.date_time
# 2	HeartRate_1.heart_rate
# 3	Corsi_1.binary_result
# 4	Corsi_1.highest_corsi_span
# 5	Corsi_1.num_of_items
# 6	Corsi_1.sequence_number
# 7	Corsi_1.trial
# 8	Flanker_1.flanker_code
# 9	Flanker_1.is_congruent
# 10	Flanker_1.response_time
# 11	Flanker_1.result
# 12	Flanker_1.trial
# 13	StudyGroup.study_group_name
# 14	Subject.subject_number
