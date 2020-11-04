from django import forms

class CreateHeartRateForm(forms.Form):
    viewHRDateTime = forms.BooleanField(label= 'HeartRate.date_time', required = False)
    viewHRHeartRate = forms.BooleanField(label= 'HeartRate.heart_rate', required = False)
    viewSubjectNumber = forms.BooleanField(label= 'subject_number', required = False) #required = True ?
    viewSGName = forms.BooleanField(label= 'study_group_name', required = False) #required = True ?

class CreateCorsiForm(forms.Form):
    viewCBinaryResult = forms.BooleanField(label= 'Corsi.binary_result', required = False)
    viewCHighestSpan = forms.BooleanField(label= 'Corsi.highest_corsi_span', required = False)
    viewCNumOfItems = forms.BooleanField(label= 'Corsi.num_of_items', required = False)
    viewCSeqNum = forms.BooleanField(label= 'Corsi.sequence_number', required = False)
    viewCTrial = forms.BooleanField(label= 'Corsi.trial', required = False)
    viewSubjectNumber = forms.BooleanField(label= 'subject_number', required = False) #required = True ?
    viewSGName = forms.BooleanField(label= 'study_group_name', required = False) #required = True ?

class CreateFlankerForm(forms.Form):
    viewFResponseTime = forms.BooleanField(label= 'Flanker.response_time', required = False)
    viewFIsCongruent = forms.BooleanField(label= 'Flanker.is_congruent', required = False)
    viewFResult = forms.BooleanField(label= 'Flanker.result', required = False)
    viewFTrial = forms.BooleanField(label= 'Flanker.trial', required = False)
    viewSubjectNumber = forms.BooleanField(label= 'subject_number', required = False) #required = True ?
    viewSGName = forms.BooleanField(label= 'study_group_name', required = False) #required = True ?

class CreateHeartRateANDCorsi(forms.Form):
    viewHRDateTime = forms.BooleanField(label= 'HeartRate.date_time', required = False)
    viewHRHeartRate = forms.BooleanField(label= 'HeartRate.heart_rate', required = False)
    viewCBinaryResult = forms.BooleanField(label= 'Corsi.binary_result', required = False)
    viewCHighestSpan = forms.BooleanField(label= 'Corsi.highest_corsi_span', required = False)
    viewCNumOfItems = forms.BooleanField(label= 'Corsi.num_of_items', required = False)
    viewCSeqNum = forms.BooleanField(label= 'Corsi.sequence_number', required = False)
    viewCTrial = forms.BooleanField(label= 'Corsi.trial', required = False)
    viewSubjectNumber = forms.BooleanField(label= 'subject_number', required = False) #required = True ?
    viewSGName = forms.BooleanField(label= 'study_group_name', required = False) #required = True ?

class CreateHeartRateANDFlanker(forms.Form):
    viewHRDateTime = forms.BooleanField(label= 'HeartRate.date_time', required = False)
    viewHRHeartRate = forms.BooleanField(label= 'HeartRate.heart_rate', required = False)
    viewFResponseTime = forms.BooleanField(label= 'Flanker.response_time', required = False)
    viewFIsCongruent = forms.BooleanField(label= 'Flanker.is_congruent', required = False)
    viewFResult = forms.BooleanField(label= 'Flanker.result', required = False)
    viewFTrial = forms.BooleanField(label= 'Flanker.trial', required = False)
    viewSubjectNumber = forms.BooleanField(label= 'subject_number', required = False) #required = True ?
    viewSGName = forms.BooleanField(label= 'study_group_name', required = False) #required = True ?

class CreateCorsiANDFlanker(forms.Form):
    viewCBinaryResult = forms.BooleanField(label= 'Corsi.binary_result', required = False)
    viewCHighestSpan = forms.BooleanField(label= 'Corsi.highest_corsi_span', required = False)
    viewCNumOfItems = forms.BooleanField(label= 'Corsi.num_of_items', required = False)
    viewCSeqNum = forms.BooleanField(label= 'Corsi.sequence_number', required = False)
    viewCTrial = forms.BooleanField(label= 'Corsi.trial', required = False)
    viewFResponseTime = forms.BooleanField(label= 'Flanker.response_time', required = False)
    viewFIsCongruent = forms.BooleanField(label= 'Flanker.is_congruent', required = False)
    viewFResult = forms.BooleanField(label= 'Flanker.result', required = False)
    viewFTrial = forms.BooleanField(label= 'Flanker.trial', required = False)
    viewSubjectNumber = forms.BooleanField(label= 'subject_number', required = False) #required = True ?
    viewSGName = forms.BooleanField(label= 'study_group_name', required = False) #required = True ?

class CreateALL(forms.Form):
    viewHRDateTime = forms.BooleanField(label= 'HeartRate.date_time', required = False)
    viewHRHeartRate = forms.BooleanField(label= 'HeartRate.heart_rate', required = False)
    viewCBinaryResult = forms.BooleanField(label= 'Corsi.binary_result', required = False)
    viewCHighestSpan = forms.BooleanField(label= 'Corsi.highest_corsi_span', required = False)
    viewCNumOfItems = forms.BooleanField(label= 'Corsi.num_of_items', required = False)
    viewCSeqNum = forms.BooleanField(label= 'Corsi.sequence_number', required = False)
    viewCTrial = forms.BooleanField(label= 'Corsi.trial', required = False)
    viewFResponseTime = forms.BooleanField(label= 'Flanker.response_time', required = False)
    viewFIsCongruent = forms.BooleanField(label= 'Flanker.is_congruent', required = False)
    viewFResult = forms.BooleanField(label= 'Flanker.result', required = False)
    viewFTrial = forms.BooleanField(label= 'Flanker.trial', required = False)
    viewSubjectNumber = forms.BooleanField(label= 'subject_number', required = False) #required = True ?
    viewSGName = forms.BooleanField(label= 'study_group_name', required = False) #required = True ?

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
class CreateHRFilterForm(forms.Form):
    filterHRDateTime_symbol = forms.CharField(label='HeartRate.date_time', widget=forms.Select(choices=Integer_Symbols))
    filterHRDateTime_value = forms.CharField()


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
