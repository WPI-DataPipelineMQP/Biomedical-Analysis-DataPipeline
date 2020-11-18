from django.shortcuts import render
import json
import pandas as pd
import numpy as np 
from django.shortcuts import HttpResponse
from .forms import CreateChosenBooleanForm, CreateChosenBooleanFormWithoutDesc, CreateChosenFilterForm, CreateHeartRateForm, CreateCorsiForm, CreateFlankerForm, CreateHeartRateANDCorsi, CreateHeartRateANDFlanker, CreateCorsiANDFlanker, CreateALL
from django.http import HttpResponseRedirect
from django.core import serializers
from django.shortcuts import redirect
from . import viewsHelper as ViewHelper
from django.db import connection
from .database import DBClient
from .forms import CreateHeartRateForm, CreateCorsiForm, CreateFlankerForm, CreateHeartRateANDCorsi
from .forms import CreateHeartRateANDFlanker, CreateCorsiANDFlanker, CreateALL

# Create your views here.

def home(request):
    return render(request, 'datapipeline/home.html', {'myCSS': 'home.css'})

def studySelection(request):
    study_fields = []
    args = {
        'selectors': 'study_name, study_description, study_id',
        'from': 'Study',
        'join-type': None,
        'join-stmt': None,
        'where': None,
        'group-by': None,
        'order-by': None
    }
    result = DBClient.executeQuery(args, 1)
    for (study_name, study_description, study_id) in result:  # cursor:
        studies_dict = {}
        studies_dict["name"] = study_name
        studies_dict["description"] = study_description
        studies_dict["id"] = study_id
        study_fields.append(studies_dict)
    
    request.session['study_fields'] = study_fields

    if request.method == 'POST':

        studies_form = CreateChosenBooleanForm(request.POST, customFields=study_fields)

        studies_data = {}

        if studies_form.is_valid():
            for i, field in enumerate(studies_form.getAllFields()):
                studies_data[i] = {
                    'name': study_fields[i]['name'],
                    'value': field[1],
                    'id': study_fields[i]["id"]
                }

        #gets the names to be printed out                                
        study_names = ViewHelper.getNameList(studies_data)
        request.session['study_names'] = study_names
        request.session['studies_data'] = studies_data

        return HttpResponseRedirect('/dataSelection')
        #return render(request, 'datapipeline/studySelection.html', context)

    studies_form = CreateChosenBooleanForm(customFields=study_fields)

    context = {
        'studies_form': studies_form,
        'myCSS': 'studySelection.css'
    }
    return render(request, 'datapipeline/studySelection.html', context)


def dataSelection(request):

    studies_data = []
    if 'studies_data' in request.session:
        studies_data = request.session['studies_data']

    study_ids_forquery = ''
    j  = 0
    for key in studies_data:
        study = studies_data[key]
        if j == 0:
            study_ids_forquery += 'study_id = ' + str(study['id'])
            j =  1
        else:
            study_ids_forquery += "OR study_id = '" + str(study['id'])

    args = {
        'selectors': 'DataCategory.dc_table_name',
        'from': 'DataCategory',
        'join-type': 'JOIN',
        'join-stmt': 'DataCategoryStudyXref ON DataCategory.data_category_id = DataCategoryStudyXref.data_category_id WHERE ' + study_ids_forquery,
        'where': None,
        'group-by': None,
        'order-by': None
    }
    result = DBClient.executeQuery(args, 1)
    data_categories = []
    for table_name in result:  # cursor:
        tables_dict = {}
        tables_dict["name"] = table_name[0]
        data_categories.append(tables_dict)

    #study group
    args = {
        'selectors': 'study_group_name',
        'from': 'StudyGroup',
        'join-type': None,
        'join-stmt': None,
        'where': study_ids_forquery,
        'group-by': None,
        'order-by': None
    }
    result = DBClient.executeQuery(args, 1)
    study_groups = []
    for study_group_name in result:
        studygroups_dict = {}
        studygroups_dict["name"] = study_group_name[0]
        study_groups.append(studygroups_dict)


    request.session['data_categories'] = data_categories
    request.session['study_groups'] = study_groups

    if request.method == 'POST':
        categories_form = CreateChosenBooleanFormWithoutDesc(request.POST, customFields=request.session['data_categories'])
        study_groups_form = CreateChosenBooleanFormWithoutDesc(request.POST, customFields=request.session['study_groups'])

        #process the data
        categories_data = {}
        if categories_form.is_valid():
            for i, field in enumerate(categories_form.getAllFields()):
                categories_data[i] = {
                    'name': data_categories[i]['name'],
                    'value': field[1]
                }

        category_names = ViewHelper.getNameList(categories_data)
        request.session['category_names'] = category_names

        study_groups_data = {}
        if study_groups_form.is_valid():
            for i, field in enumerate(study_groups_form.getAllFields()):
                study_groups_data[i] = {
                    'name': study_groups[i]['name'],
                    'value': field[1]
                }

        study_group_names = ViewHelper.getNameList(study_groups_data)
        request.session['study_group_names'] = study_group_names


        return HttpResponseRedirect('/dataSelection-2')


    categories_form = CreateChosenBooleanFormWithoutDesc(customFields=data_categories)
    study_groups_form = CreateChosenBooleanFormWithoutDesc(customFields=study_groups)

    context = {
        'myCSS': 'dataSelection.css',
        'study_names': request.session['study_names'],
        'categories_form': categories_form,
        'study_groups_form': study_groups_form
    }
       
    print('\nGot Data Selection Request\n')
    
    return render(request, 'datapipeline/dataSelection.html', context)

def dataSelectionContinued(request):

    category_names = []
    if 'category_names' in request.session:
        category_names = request.session['category_names']

    columns = []
    for table in category_names:
        args = {
            'selectors': '*',
            'from': 'INFORMATION_SCHEMA.COLUMNS',
            'join-type': None,
            'join-stmt': None,
            'where': "TABLE_NAME = N'"+table+"'",
            'group-by': None,
            'order-by': None
        }
        result = DBClient.executeQuery(args, 1)
        for column_name in result:
            if(column_name[3] == "data_id" or column_name[3] == "subject_id"):
                pass
            else:
                column_dict = {}
                column_dict["name"] = column_name[3]
                column_dict["table"] = table
                columns.append(column_dict)

    #add these because they are always shown by default
    subject_num_dict = {"name": "subject_number", "table": "Subject"}
    study_group_dict = {"name": "study_group_name", "table": "StudyGroup"}
    columns.append(subject_num_dict)
    columns.append(study_group_dict)

    request.session['columns'] = columns
    print(columns)

    if request.method == 'POST':
        attributes_form = CreateChosenBooleanFormWithoutDesc(request.POST, customFields=request.session['columns'])
        filters_form = CreateChosenFilterForm(request.POST, customFields=request.session['columns'])

        #process the data
        attribute_data = {}
        if attributes_form.is_valid():
            for i, field in enumerate(attributes_form.getAllFields()):
                attribute_data[i] = {
                    'name': columns[i]['name'],
                    'value': field[1]
                }
        attribute_names = ViewHelper.getNameList(attribute_data)
        request.session['attribute_names'] = attribute_names

        filter_data = {}
        if filters_form.is_valid():
            print(columns)
            for i, field in enumerate(filters_form.getAllFields()):
                print("i: " + str(i))
                print(field)
                filter_data[i] = {
                    #'name': columns[i]['name'],
                    'name': field[0],
                    'value': field[1]
                }
        filter_names = ViewHelper.getNameList(filter_data)
        request.session['filter_names'] = filter_names


        return HttpResponseRedirect('/output')

    attributes_form = CreateChosenBooleanFormWithoutDesc(customFields=request.session['columns'])
    filters_form = CreateChosenFilterForm(customFields=request.session['columns'])

    context = {
         'myCSS': 'dataSelection.css',
         'study_names': request.session['study_names'],
         'category_names': request.session['category_names'],
         'study_group_names': request.session['study_group_names'],
         'attributes': attributes_form,
         'filters': filters_form
    }

    print('\nGot Data Selection Request\n')

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


    
