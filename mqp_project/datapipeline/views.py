from django.shortcuts import render
import json
import pandas as pd
from django.shortcuts import HttpResponse
from .forms import CreateChosenBooleanForm, CreateChosenBooleanFormWithoutDesc, CreateHeartRateForm, CreateCorsiForm, CreateFlankerForm, CreateHeartRateANDCorsi, CreateHeartRateANDFlanker, CreateCorsiANDFlanker, CreateALL
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
    study_fields = available_studies
    
    request.session['study_fields'] = study_fields
    print(request.method)
    if request.method == 'POST':
        studies_form = CreateChosenBooleanForm(request.POST, customFields=study_fields)

        #print(studies_form)
        if studies_form.is_valid():
            for field in studies_form.fields:
                print(field)
                this = studies_form.cleaned_data[field]
                print("STUDY: " + str(this))
        print('\nGot Study Selection Request\n')

        studies_data = {}
        if studies_form.is_valid():
            for field in studies_form.fields:
                studies_data[field] = {
                    'id': studies_form[field].name,
                    'name': studies_form[field].label, 
                    'value': studies_form.cleaned_data[field]
                }

        print(studies_data)

        #gets the names to be printed out                                
        study_names = ViewHelper.getNameList(studies_data)
        request.session['study_names'] = study_names

        return HttpResponseRedirect('/dataSelection')
        #return render(request, 'datapipeline/studySelection.html', context)

    studies_form = CreateChosenBooleanForm(customFields=study_fields)

    context = {
        'studies_form': studies_form,
        'myCSS': 'studySelection.css'
    }
    return render(request, 'datapipeline/studySelection.html', context)


def dataSelection(request):
    #get information from form on previous page
    #studies_form = CreateChosenBooleanForm(request.POST, customFields=request.session['study_fields'])

    #replace with query for data categories
    data_categories = [
        {
            "id": 1,
            "name":"Heart Rate"
        },
        {
            "id": 2,
            "name":"Corsi"
        },
        {
            "id": 3,
            "name":"Flanker"
        },
    ]

    #reqplace with query for study groups
    study_groups = [
        {
            "id": 1,
            "name":"Control"
        },
        {
            "id": 2,
            "name":"Experimental"
        },
    ]

    print(request.method)
    if request.method == 'POST':
        categories_form = CreateChosenBooleanFormWithoutDesc(request.POST, customFields=request.session['data_categories'])
        study_groups_form = CreateChosenBooleanFormWithoutDesc(request.POST, customFields=request.session['study_groups'])

        #process the data
        categories_data = {}
        if categories_form.is_valid():
            for field in categories_form.fields:
                categories_data[field] = {
                    'id': categories_form[field].name,
                    'name': categories_form[field].label, 
                    'value': categories_form.cleaned_data[field]
                }

        category_names = ViewHelper.getNameList(categories_data)
        request.session['category_names'] = category_names

        study_groups_data = {}
        if study_groups_form.is_valid():
            for field in study_groups_form.fields:
                study_groups_data[field] = {
                        'id': study_groups_form[field].name,
                        'name': study_groups_form[field].label, 
                        'value': study_groups_form.cleaned_data[field]
                    }

        study_group_names = ViewHelper.getNameList(study_groups_data)
        request.session['study_group_names'] = study_group_names

        return HttpResponseRedirect('/dataSelection-2')


    categories_form = CreateChosenBooleanFormWithoutDesc(customFields=data_categories)
    study_groups_form = CreateChosenBooleanFormWithoutDesc(customFields=study_groups)

    request.session['data_categories'] = data_categories
    request.session['study_groups'] = study_groups

    context = {
        'myCSS': 'dataSelection.css',
        'study_names': request.session['study_names'],
        'categories_form': categories_form,
        'study_groups_form': study_groups_form
    }
       
    print('\nGot Data Selection Request\n')
    
    return render(request, 'datapipeline/dataSelection.html', context)

def dataSelectionContinued(request):
    #raw_studies = request.POST.getlist('studies[]')
    #raw_data_categories = request.POST.getlist('categories[]')
    #raw_study_groups = request.POST.getlist('studyGroups[]')

    #studies = ViewHelper.getJSONVersion(raw_studies)
    #categories = ViewHelper.getJSONVersion(raw_data_categories)
    #sgroups = ViewHelper.getJSONVersion(raw_study_groups)

    #print("data-studies:")
    #print(studies)
    #print("data-categories:")
    #print(categories)    

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
         'study_names': request.session['study_names'],
         'category_names': request.session['category_names'],
         'study_group_names': request.session['study_group_names'],
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
    #raw_data_categories = request.POST.getlist('categories[]')
    #raw_study_groups = request.POST.getlist('studyGroups[]')
    #raw_data_attributes = request.POST.getlist('attributes[]')
    #raw_data_filters = request.POST.getlist('filters[]')

    # print("output-attr")
    # print(raw_data_attributes)
    # print("output-filters")
    # print(raw_data_filters)
    # print("output-cat")
    # print(raw_data_categories)


    #studies = getJSONVersion(raw_studies)
    #categories = ViewHelper.getJSONVersion(raw_data_categories)
    #sgroups = ViewHelper.getJSONVersion(raw_study_groups)
    #data_attributes = ViewHelper.getJSONVersion(raw_data_attributes)

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
