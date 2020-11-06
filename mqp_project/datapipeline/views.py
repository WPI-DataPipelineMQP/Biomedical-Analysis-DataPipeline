from django.shortcuts import render
import json
from .forms import CreateHeartRateForm, CreateCorsiForm, CreateFlankerForm, CreateHeartRateANDCorsi, CreateHeartRateANDFlanker, CreateCorsiANDFlanker, CreateALL
from django.http import HttpResponseRedirect

# Create your views here.
def home(request):
    return render(request, 'datapipeline/home.html', {'myCSS': 'home.css'})


def singleStudy(request):
    available_studies = [
        {
            "study_name": "Exercise IQP",
            "description": "Duis ultrices, velit vitae feugiat sagittis, ipsum dolor interdum risus, et pretium tellus nulla vitae quam. Nullam placerat dapibus lorem sit amet cursus. In ac mauris hendrerit, rutrum orci et, bibendum sem. Donec massa nisl, sagittis vel molestie elementum, semper sed leo. Nullam eros nulla, varius eget est quis, condimentum convallis quam. Praesent varius diam non libero ullamcorper, vel pulvinar erat commodo. Quisque tincidunt sollicitudin leo ut viverra."
        },
        {
            "study_name": "Covid",
            "description": "Etiam purus libero, efficitur semper dui vitae, tempus molestie est. Fusce enim tellus, placerat et dolor rutrum, volutpat consectetur ex. In vel nulla accumsan, suscipit quam ac, varius diam. Quisque sed mauris quis nulla mattis sagittis. Etiam fringilla turpis nec nisi luctus elementum. Quisque in sodales elit, sed ornare felis. Quisque eget venenatis est, nec dictum tortor. Donec ultrices odio massa, quis vestibulum nulla blandit non. Cras ut fermentum velit. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse auctor neque id neque bibendum sagittis. Maecenas ac nunc eu risus congue ultricies."
        },
    ]
    context = {
        'studies': available_studies,
        'myCSS' : 'singleStudy.css'
    }
    
    print('\nGot Single Study Request\n')
    
    return render(request, 'datapipeline/singleStudy.html', context)



def crossStudy(request):
    available_studies = [
        {
            "study_name": "Exercise IQP",
            "description": "Duis ultrices, velit vitae feugiat sagittis, ipsum dolor interdum risus, et pretium tellus nulla vitae quam. Nullam placerat dapibus lorem sit amet cursus. In ac mauris hendrerit, rutrum orci et, bibendum sem. Donec massa nisl, sagittis vel molestie elementum, semper sed leo. Nullam eros nulla, varius eget est quis, condimentum convallis quam. Praesent varius diam non libero ullamcorper, vel pulvinar erat commodo. Quisque tincidunt sollicitudin leo ut viverra."
        },
        {
            "study_name": "Covid",
            "description": "Etiam purus libero, efficitur semper dui vitae, tempus molestie est. Fusce enim tellus, placerat et dolor rutrum, volutpat consectetur ex. In vel nulla accumsan, suscipit quam ac, varius diam. Quisque sed mauris quis nulla mattis sagittis. Etiam fringilla turpis nec nisi luctus elementum. Quisque in sodales elit, sed ornare felis. Quisque eget venenatis est, nec dictum tortor. Donec ultrices odio massa, quis vestibulum nulla blandit non. Cras ut fermentum velit. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse auctor neque id neque bibendum sagittis. Maecenas ac nunc eu risus congue ultricies."
        },
    ]
    context = {
        'studies': available_studies,
        'myCSS' : 'singleStudy.css'
    }
    
    print('\nGot Cross Study Request\n')
    
    return render(request, 'datapipeline/crossStudy.html', context)


def getJSONVersion(raw_list):
    dictionaries = []
    
    for raw_dict in raw_list:
        reformatted = str(raw_dict).replace("'", '"')
        study = json.loads(reformatted)
        dictionaries.append(study)
        
    return dictionaries


def dataSelection(request):
    raw_studies = request.POST.getlist('studies[]')
    studies = getJSONVersion(raw_studies)

    #replace these with queries below
    data_categories = [
        {
            "name":"Heart Rate"
        },
        {
            "name":"Corsi"
        },
        {
            "name":"Flanker"
        },
    ]

    study_groups = [
        {
            "name":"Control"
        },
        {
            "name":"Experimental"
        },
    ]
    
    context = {
        'myCSS': 'dataSelection.css',
        'studies': studies,
        'categories': data_categories,
        'sgroups': study_groups
    }
       
    print('\nGot Data Selection Request\n')
    
    return render(request, 'datapipeline/dataSelection.html', context)

def dataSelectionContinued(request):
    raw_studies = request.POST.getlist('studies[]')
    raw_data_categories = request.POST.getlist('categories[]')
    raw_study_groups = request.POST.getlist('studyGroups[]')

    studies = getJSONVersion(raw_studies)
    categories = getJSONVersion(raw_data_categories)
    sgroups = getJSONVersion(raw_study_groups)
    #
    # tables = ['HeartRate']  # Get this from the first data-selection screen
    # data_attributes = pickAttributesToShowUsers(tables)


    tables = ['HeartRate'] #Get this from the first data-selection screen
    if request.method == 'POST':
        if ('HeartRate' in tables) and ('Corsi' not in tables) and ('Flanker' not in tables):
            attributeForm = CreateHeartRateForm(request.POST)
        elif ('HeartRate' not in tables) and ('Corsi' in tables) and ('Flanker' not in tables):
            attributeForm = CreateCorsiForm(request.POST)
        elif ('HeartRate' not in tables) and ('Corsi' not in tables) and ('Flanker' in tables):
            attributeForm = CreateFlankerForm(request.POST)
        elif ('HeartRate' in tables) and ('Corsi' in tables) and ('Flanker' not in tables):
            attributeForm = CreateHeartRateANDCorsi(request.POST)
        elif ('HeartRate' in tables) and ('Corsi' not in tables) and ('Flanker' in tables):
            attributeForm = CreateHeartRateANDFlanker(request.POST)
        elif ('HeartRate' not in tables) and ('Corsi' in tables) and ('Flanker' in tables):
            attributeForm = CreateCorsiANDFlanker(request.POST)
        else:
            attributeForm = CreateALL(request.POST)
        if attributeForm.is_valid():
            viewHRDateTime = attributeForm.cleaned_data['viewHRDateTime']
            viewHRHeartRate = attributeForm.cleaned_data['viewHRHeartRate']
            viewSubjectNumber = attributeForm.cleaned_data['viewSubjectNumber']
            viewSGName = attributeForm.cleaned_data['viewSGName']
            filterValueHRDateTime = attributeForm.cleaned_data['filterValueHRDateTime']

            print("DATETIME: " + str(viewHRDateTime) + "\n")
            print("HEARTREATE: " + str(viewHRHeartRate) + "\n")
            print("SUBJECT: " + str(viewSubjectNumber) + "\n")
            print("STUDYGROUP: " + str(viewSGName) + "\n")
            print("TEXT: " + filterValueHRDateTime + "\n")

            if attributeForm.is_valid():
                return HttpResponseRedirect('/dataSelection-2')
        else:
            print("invalid")
    else:
        if ('HeartRate' in tables) and ('Corsi' not in tables) and ('Flanker' not in tables):
            attributeForm = CreateHeartRateForm(request.POST)
        elif ('HeartRate' not in tables) and ('Corsi' in tables) and ('Flanker' not in tables):
            attributeForm = CreateCorsiForm(request.POST)
        elif ('HeartRate' not in tables) and ('Corsi' not in tables) and ('Flanker' in tables):
            attributeForm = CreateFlankerForm(request.POST)
        elif ('HeartRate' in tables) and ('Corsi' in tables) and ('Flanker' not in tables):
            attributeForm = CreateHeartRateANDCorsi(request.POST)
        elif ('HeartRate' in tables) and ('Corsi' not in tables) and ('Flanker' in tables):
            attributeForm = CreateHeartRateANDFlanker(request.POST)
        elif ('HeartRate' not in tables) and ('Corsi' in tables) and ('Flanker' in tables):
            attributeForm = CreateCorsiANDFlanker(request.POST)
        else:
            attributeForm = CreateALL(request.POST)

    context = {
         'myCSS': 'dataSelection.css',
         'studies': studies,
         'categories': categories,
         'sgroups': sgroups,
         'form': attributeForm,
    #     'attributes': data_attributes,
    #     'filters': data_attributes,
    }

    return render(request, 'datapipeline/dataSelection-2.html', context)


def pickAttributesToShowUsers(tables):
    if ('HeartRate' in tables) and ('Corsi' not in tables) and ('Flanker' not in tables):
        data_attributes = [
            {"name": "HeartRate.date_time"},
            {"name": "HeartRate.heart_rate"},
            {"name": "subject_number"},
            {"name": "study_group_name"},
        ]
    elif ('HeartRate' not in tables) and ('Corsi' in tables) and ('Flanker' not in tables):
        data_attributes = [
            {"name": "Corsi.binary_result"},
            {"name": "Corsi.highest_corsi_span"},
            {"name": "Corsi.num_of_items"},
            {"name": "Corsi.sequence_number"},
            {"name": "Corsi.trial"},
            {"name": "subject_number"},
            {"name": "study_group_name"},
        ]
    elif ('HeartRate' not in tables) and ('Corsi' not in tables) and ('Flanker' in tables):
        data_attributes = [
            {"name": "Flanker.response_time"},
            {"name": "Flanker.is_congruent"},
            {"name": "Flanker.result"},
            {"name": "Flanker.trial"},
            {"name": "subject_number"},
            {"name": "study_group_name"},
        ]
    elif ('HeartRate' in tables) and ('Corsi' in tables) and ('Flanker' not in tables):
        data_attributes = [
            {"name": "HeartRate.date_time"},
            {"name": "HeartRate.heart_rate"},
            {"name": "Corsi.binary_result"},
            {"name": "Corsi.highest_corsi_span"},
            {"name": "Corsi.num_of_items"},
            {"name": "Corsi.sequence_number"},
            {"name": "Corsi.trial"},
            {"name": "subject_number"},
            {"name": "study_group_name"},
        ]
    elif ('HeartRate' in tables) and ('Corsi' not in tables) and ('Flanker' in tables):
        data_attributes = [
            {"name": "HeartRate.date_time"},
            {"name": "HeartRate.heart_rate"},
            {"name": "Flanker.response_time"},
            {"name": "Flanker.is_congruent"},
            {"name": "Flanker.result"},
            {"name": "Flanker.trial"},
            {"name": "subject_number"},
            {"name": "study_group_name"},
        ]
    elif ('HeartRate' not in tables) and ('Corsi' in tables) and ('Flanker' in tables):
        data_attributes = [
            {"name": "Corsi.binary_result"},
            {"name": "Corsi.highest_corsi_span"},
            {"name": "Corsi.num_of_items"},
            {"name": "Corsi.sequence_number"},
            {"name": "Corsi.trial"},
            {"name": "Flanker.response_time"},
            {"name": "Flanker.is_congruent"},
            {"name": "Flanker.result"},
            {"name": "Flanker.trial"},
            {"name": "subject_number"},
            {"name": "study_group_name"},
        ]
    else:
        data_attributes = [
            {"name": "HeartRate.date_time"},
            {"name": "HeartRate.heart_rate"},
            {"name": "Corsi.binary_result"},
            {"name": "Corsi.highest_corsi_span"},
            {"name": "Corsi.num_of_items"},
            {"name": "Corsi.sequence_number"},
            {"name": "Corsi.trial"},
            {"name": "Flanker.response_time"},
            {"name": "Flanker.is_congruent"},
            {"name": "Flanker.result"},
            {"name": "Flanker.trial"},
            {"name": "subject_number"},
            {"name": "study_group_name"},
        ]
    return data_attributes
