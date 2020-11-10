from django.shortcuts import render
import json
import pandas as pd
from django.shortcuts import HttpResponse
from .forms import CreateChosenBooleanForm, CreateHeartRateForm, CreateCorsiForm, CreateFlankerForm, CreateHeartRateANDCorsi, CreateHeartRateANDFlanker, CreateCorsiANDFlanker, CreateALL
from django.http import HttpResponseRedirect
from django.core import serializers
from .viewsHelper import ViewHelper
# Create your views here.

def home(request):
    return render(request, 'datapipeline/home.html', {'myCSS': 'home.css'})

def studySelection(request):
    available_studies = [
        {
            "id": 1,
            "name": "Exercise IQP",
            "description": "Duis ultrices, velit vitae feugiat sagittis, ipsum dolor interdum risus, et pretium tellus nulla vitae quam. Nullam placerat dapibus lorem sit amet cursus. In ac mauris hendrerit, rutrum orci et, bibendum sem. Donec massa nisl, sagittis vel molestie elementum, semper sed leo. Nullam eros nulla, varius eget est quis, condimentum convallis quam. Praesent varius diam non libero ullamcorper, vel pulvinar erat commodo. Quisque tincidunt sollicitudin leo ut viverra."
        },
        {
            "id": 2,
            "name": "Covid",
            "description": "Etiam purus libero, efficitur semper dui vitae, tempus molestie est. Fusce enim tellus, placerat et dolor rutrum, volutpat consectetur ex. In vel nulla accumsan, suscipit quam ac, varius diam. Quisque sed mauris quis nulla mattis sagittis. Etiam fringilla turpis nec nisi luctus elementum. Quisque in sodales elit, sed ornare felis. Quisque eget venenatis est, nec dictum tortor. Donec ultrices odio massa, quis vestibulum nulla blandit non. Cras ut fermentum velit. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Suspendisse auctor neque id neque bibendum sagittis. Maecenas ac nunc eu risus congue ultricies."
        },
    ]

    # CHANGE ONCE WE CAN QUERY THE DATABASE
    fields = available_studies
    
    form = CreateChosenBooleanForm(customFields=fields)
    context = {
        'form': form,
        'myCSS' : 'studySelection.css'
    }
    print('\nGot Study Selection Request\n')
    
    return render(request, 'datapipeline/studySelection.html', context)



def dataSelection(request):
    #raw_studies = request.POST.getlist('studies[]')
    #studies = ViewHelper.getJSONVersion(raw_studies)

    #print("Fay-studies:")
    #print(studies)

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
    
    print(request.POST)
    #studyForm = CreateChosenBooleanForm(request.POST)

    context = {
        'myCSS': 'dataSelection.css',
        #'studies': studies,
        'categories': data_categories,
        'sgroups': study_groups
    }
       
    print('\nGot Data Selection Request\n')
    
    return render(request, 'datapipeline/dataSelection.html', context)

def dataSelectionContinued(request):
    #raw_studies = request.POST.getlist('studies[]')
    raw_data_categories = request.POST.getlist('categories[]')
    raw_study_groups = request.POST.getlist('studyGroups[]')

    #studies = ViewHelper.getJSONVersion(raw_studies)
    categories = ViewHelper.getJSONVersion(raw_data_categories)
    sgroups = ViewHelper.getJSONVersion(raw_study_groups)

    #print("data-studies:")
    #print(studies)
    print("data-categories:")
    print(categories)

    tables = ['HeartRate']  # Get this from the first data-selection screen
    #data_attributes = pickAttributesToShowUsers(tables)
    data_attributes = [
        {"name": "HeartRate.date_time"},
        {"name": "HeartRate.heart_rate"},
        {"name": "subject_number"},
        {"name": "study_group_name"},
    ]
    print("dataattr0:")
    print(data_attributes[0])
    # tables = ['HeartRate'] #Get this from the first data-selection screen
    # if request.method == 'POST':
    #     if ('HeartRate' in tables) and ('Corsi' not in tables) and ('Flanker' not in tables):
    #         attributeForm = CreateHeartRateForm(request.POST)
    #     elif ('HeartRate' not in tables) and ('Corsi' in tables) and ('Flanker' not in tables):
    #         attributeForm = CreateCorsiForm(request.POST)
    #     elif ('HeartRate' not in tables) and ('Corsi' not in tables) and ('Flanker' in tables):
    #         attributeForm = CreateFlankerForm(request.POST)
    #     elif ('HeartRate' in tables) and ('Corsi' in tables) and ('Flanker' not in tables):
    #         attributeForm = CreateHeartRateANDCorsi(request.POST)
    #     elif ('HeartRate' in tables) and ('Corsi' not in tables) and ('Flanker' in tables):
    #         attributeForm = CreateHeartRateANDFlanker(request.POST)
    #     elif ('HeartRate' not in tables) and ('Corsi' in tables) and ('Flanker' in tables):
    #         attributeForm = CreateCorsiANDFlanker(request.POST)
    #     else:
    #         attributeForm = CreateALL(request.POST)
    #     if attributeForm.is_valid():
    #         viewHRDateTime = attributeForm.cleaned_data['viewHRDateTime']
    #         viewHRHeartRate = attributeForm.cleaned_data['viewHRHeartRate']
    #         viewSubjectNumber = attributeForm.cleaned_data['viewSubjectNumber']
    #         viewSGName = attributeForm.cleaned_data['viewSGName']
    #         filterHRDateTime = attributeForm.cleaned_data['filterHRDateTime']
    #         filterHRHeartRate = attributeForm.cleaned_data['filterHRHeartRate']
    #         filterSubjectNumber = attributeForm.cleaned_data['filterSubjectNumber']
    #         filterSGName = attributeForm.cleaned_data['filterSGName']
    #
    #         filterSymHRDateTime = attributeForm.cleaned_data['filterSymHRDateTime']
    #         filterSymHRHeartRate = attributeForm.cleaned_data['filterSymHRHeartRate']
    #         filterSymSubjectNumber = attributeForm.cleaned_data['filterSymSubjectNumber']
    #         filterSymSGName = attributeForm.cleaned_data['filterSymSGName']
    #
    #         filterValueHRDateTime = attributeForm.cleaned_data['filterValueHRDateTime']
    #         filterValueHRHeartRate = attributeForm.cleaned_data['filterValueHRHeartRate']
    #         filterValueSubjectNumber = attributeForm.cleaned_data['filterValueSubjectNumber']
    #         filterValueSGName = attributeForm.cleaned_data['filterValueSGName']
    #
    #         print("DATETIME: " + str(viewHRDateTime) + "\n")
    #         print("HEARTREATE: " + str(viewHRHeartRate) + "\n")
    #         print("SUBJECT: " + str(viewSubjectNumber) + "\n")
    #         print("STUDYGROUP: " + str(viewSGName) + "\n")
    #         print("TEXT: " + filterValueHRDateTime + "\n")
    #
    #         return HttpResponseRedirect('/output')
    #     else:
    #         print("invalid")
    # else:
    #     if ('HeartRate' in tables) and ('Corsi' not in tables) and ('Flanker' not in tables):
    #         attributeForm = CreateHeartRateForm(request.POST)
    #     elif ('HeartRate' not in tables) and ('Corsi' in tables) and ('Flanker' not in tables):
    #         attributeForm = CreateCorsiForm(request.POST)
    #     elif ('HeartRate' not in tables) and ('Corsi' not in tables) and ('Flanker' in tables):
    #         attributeForm = CreateFlankerForm(request.POST)
    #     elif ('HeartRate' in tables) and ('Corsi' in tables) and ('Flanker' not in tables):
    #         attributeForm = CreateHeartRateANDCorsi(request.POST)
    #     elif ('HeartRate' in tables) and ('Corsi' not in tables) and ('Flanker' in tables):
    #         attributeForm = CreateHeartRateANDFlanker(request.POST)
    #     elif ('HeartRate' not in tables) and ('Corsi' in tables) and ('Flanker' in tables):
    #         attributeForm = CreateCorsiANDFlanker(request.POST)
    #     else:
    #         attributeForm = CreateALL(request.POST)
    #
    # # assuming obj is a model instance
    # serialized_obj = serializers.serialize('json', [attributeForm, ])

    context = {
         'myCSS': 'dataSelection.css',
         #'studies': studies,
         'categories': categories,
         'sgroups': sgroups,
         'attributes': data_attributes,
         'filters': data_attributes
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

def output(request):
    #raw_studies = request.POST.getlist('studies[]')
    raw_data_categories = request.POST.getlist('categories[]')
    raw_study_groups = request.POST.getlist('studyGroups[]')
    raw_data_attributes = request.POST.getlist('attributes[]')
    raw_data_filters = request.POST.getlist('filters[]')

    print("output-attr")
    print(raw_data_attributes)
    print("output-filters")
    print(raw_data_filters)
    print("output-cat")
    print(raw_data_categories)


    #studies = getJSONVersion(raw_studies)
    categories = ViewHelper.getJSONVersion(raw_data_categories)
    sgroups = ViewHelper.getJSONVersion(raw_study_groups)
    data_attributes = ViewHelper.getJSONVersion(raw_data_attributes)

    data = pd.read_csv('1_fitbit.csv')
    data_html = data.to_html()
    return HttpResponse(data_html)

    # context = {
    #      'myCSS': 'dataSelection.css',
    #      #'studies': studies,
    #      'categories': categories,
    #      'sgroups': sgroups,
    #      #'form': attributeForm,
    #      'attributes': data_attributes,
    # #     'filters': data_attributes,
    # }
    #
    # return render(request, 'datapipeline/output.html', context)
