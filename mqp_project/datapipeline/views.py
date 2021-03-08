

from django.shortcuts import render
import json
import pandas as pd
import numpy as np 
import csv
from django.shortcuts import HttpResponse
from sqlalchemy import create_engine
from django.conf import settings
from django.contrib import messages
from .forms import CreateChosenBooleanForm, CreateChosenBooleanFormWithoutDesc, CreateChosenFilterForm
from django.http import HttpResponseRedirect
from django.core import serializers
from django.shortcuts import redirect
from .viewHelpers import viewsHelper as ViewHelper
from uploader.viewHelpers import Helper as UploadHelper
from django.db import connection
from .database import DBClient, DBHandler
from django.db.models import Q
from .models import Study

######################################
# Input: HTTPRequest
# Returns: HTTPResponse
# Description: Returns to the dashboard, removes documents in the uploader if there are any
######################################
def home(request):
    UploadHelper.deleteAllDocuments()
    return render(request, 'datapipeline/home.html', {'myCSS': 'home.css'})

######################################
# Input: HTTPRequest
# Returns: HTTPResponse
# Description: Creates form listing studies for template studySelection.html
#  then gets selected study's data categories and study ID to display for next page
######################################
def studySelection(request):
    UploadHelper.deleteAllDocuments()
    study_fields = []

    #Get list of studies available to user, based on permissions
    studies = Study.objects.filter(
        ~(Q(visibility="Private") & ~Q(owner=request.user.id))
    )

    #Display form with study information
    for study in studies:
        studies_dict = {}
        studies_dict["name"] = study.study_name
        studies_dict["description"] = study.study_description
        studies_dict["id"] = study.study_id
        study_fields.append(studies_dict)
    
    #save dictionary of studies to the session
    request.session['study_fields'] = study_fields

    #create dynamic form with the studies
    studies_form = CreateChosenBooleanForm(customFields=study_fields)
    
    #this is passed to the template so the form and css can be displayed when the webpage is loaded
    context = {
        'studies_form': studies_form,
        'myCSS': 'studySelection.css',
    }

    #When form is submitted
    if request.method == 'POST':

        #create the dynamic form
        studies_form = CreateChosenBooleanForm(request.POST, customFields=study_fields)
        
        #gather the data from the form
        studies_data = {}
        if studies_form.is_valid():
            for i, field in enumerate(studies_form.getAllFields()):
                #name - name of study
                #value - true if checked, false otherwise
                #id - study ID
                studies_data[i] = {
                    'name': study_fields[i]['name'],
                    'value': field[1],
                    'id': study_fields[i]["id"]
                }

        # MAKING THE QUERY TO USE
        study_ids_forquery = ''
        for i, key in enumerate(studies_data):
            study = studies_data[key]
            
            if study.get('value') is True:
                if study_ids_forquery != '':
                    study_ids_forquery += 'OR '
                
                if i == (len(studies_data) - 1):
                    study_ids_forquery += 'study_id = {}'.format(study['id'])
                    
                else:
                    study_ids_forquery += 'study_id = {} '.format(study['id'])
        
        #gets the study names to be printed out       
        study_names = ViewHelper.getNameList(studies_data, True)

        #checks if any studies have been selected
        if len(study_names) > 0:
                    
            #if so, move on to next page  
            data_categories = DBHandler.getDataCategoriesOfStudies(study_ids_forquery)
            
            study_groups = DBHandler.getStudyGroupsOfStudies(study_ids_forquery)
            
            request.session['study_names'] = study_names
            request.session['data_categories'] = data_categories
            request.session['study_groups'] = study_groups

            return HttpResponseRedirect('/dataSelection')

        #if not, show error message
        else:
            messages.error(request, 'Please select at least one study to start analysis.')
            return redirect('/study_selection')
    
    return render(request, 'datapipeline/studySelection.html', context)


######################################
# Input: HTTPRequest
# Returns: HTTPResponse
# Description: Creates form listing data categories and study groups for template dataSelection.html
#  then saves selected data categories and study groups to session
######################################
def dataSelection(request):

    data_categories = []
    study_groups = []
    
    #if there are data categories and study groups saved to the session, get them
    if 'data_categories' in request.session:
        data_categories = request.session['data_categories']
        
    if 'study_groups' in request.session:
        study_groups = request.session['study_groups']

    #create boolean forms of data categories and study groups
    categories_form = CreateChosenBooleanFormWithoutDesc(customFields=data_categories)
    study_groups_form = CreateChosenBooleanFormWithoutDesc(customFields=study_groups)

    context = {
        'myCSS': 'dataSelection.css',
        'study_names': request.session['study_names'],
        'categories_form': categories_form,
        'study_groups_form': study_groups_form,
    }

    #When form is submitted
    if request.method == 'POST':

        #create forms
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

        study_groups_data = {}
        if study_groups_form.is_valid():
            for i, field in enumerate(study_groups_form.getAllFields()):
                study_groups_data[i] = {
                    'name': study_groups[i]['name'],
                    'value': field[1]
                }
                
        #create list of names
        category_names = ViewHelper.getNameList(categories_data)
        study_group_names = ViewHelper.getNameList(study_groups_data)
        
        print("MY STUDY GROUPS\n")
        print(study_group_names)

        #checks if at least one category and study group has been selected
        if len(category_names) <= 0:
            #if not, show error message
            messages.error(request, 'Please select at least one data category.')
            return redirect('datapipeline-dataSelection')

        if len(study_group_names) <= 0:
            messages.error(request, 'Please select at least one study group.')
            return redirect('datapipeline-dataSelection')

        #save to the session
        request.session['category_names'] = category_names
        request.session['study_group_names'] = study_group_names

        return HttpResponseRedirect('/dataSelection-2')

       
    print('\nGot Data Selection Request\n')
    
    return render(request, 'datapipeline/dataSelection.html', context)


######################################
# Input: HTTPRequest
# Returns: HTTPResponse
# Description: Creates form listing attributes and filters for template dataSelection-2.html
#  then saves selected attributes and filters to session
######################################
def dataSelectionContinued(request):
    category_names = []

    #get data category names if still saved in session
    if 'category_names' in request.session:
        category_names = request.session['category_names']
    
    columnsForAttributeList = []
    columnsForFiltersList = []

    #create list of attributes in each of the tables
    for table in category_names:
        column_dict = {}
        result = DBClient.getTableColumns(table) #get all attributes from selected data categories

        #add the columns we need to lists so we can add them to the form
        for column_name in result:
            if(column_name == "data_id" or column_name == "subject_id" or column_name == "doc_id"):
                pass
            
            else:
                column_dict = {}
                column_dict["name"] = "{}.{}".format(table, column_name)
                column_dict["table"] = table
                #column_dict["display"] = "{}.{}".format(table, column_name[3])
                columnsForAttributeList.append(column_dict)
                columnsForFiltersList.append(column_dict)

    #add subject number and study group because they are always shown by default
    subject_num_dict = {"name": "subject_number", "table": "Subject"}
    study_group_dict = {"name": "study_group_name", "table": "StudyGroup"}
    columnsForAttributeList.append(subject_num_dict)
    columnsForAttributeList.append(study_group_dict)
    columnsForFiltersList.append(subject_num_dict)

    request.session['columnsForAttributeList'] = columnsForAttributeList
    request.session['columnsForFiltersList'] = columnsForFiltersList

    #create the forms
    attributes_form = CreateChosenBooleanFormWithoutDesc(customFields=request.session['columnsForAttributeList'])
    filters_form = CreateChosenFilterForm(customFields=request.session['columnsForFiltersList'])

    context = {
         'myCSS': 'dataSelection-2.css',
         'study_names': request.session['study_names'],
         'category_names': request.session['category_names'],
         'study_group_names': request.session['study_group_names'],
         'attributes': attributes_form,
         'filters': filters_form,
         'error': False
    }

    #When form is submitted
    if request.method == 'POST':
        attributes_form = CreateChosenBooleanFormWithoutDesc(request.POST, customFields=request.session['columnsForAttributeList'])
        filters_form = CreateChosenFilterForm(request.POST, customFields=request.session['columnsForFiltersList'])

        #process the attribute data
        attribute_data = {}
        if attributes_form.is_valid():
            for i, field in enumerate(attributes_form.getAllFields()):
                attribute_data[i] = {
                    'name': columnsForAttributeList[i]['name'],
                    'value': field[1]
                }

        #create list of attribute names
        attribute_names = ViewHelper.getNameList(attribute_data)

        #checks if at least one attribute has been selected
        if len(attribute_names) <= 0:
            #if not, show error message
            messages.error(request, 'Please select at least one attribute.')
            return redirect('datapipeline-dataSelection-2')

        #process the filter data
        filter_data = {}
        if filters_form.is_valid():
            for i, field in enumerate(filters_form.getAllFields()):
                filter_data[i] = {
                    #'name': columns[i]['name'],
                    'name': field[0],
                    'value': field[1]
                }

        #get the filter names and their values
        filter_names = ViewHelper.getNameList(filter_data)
        filter_values = ViewHelper.getChosenFilters(filter_data)

        #save data to the session
        request.session['attribute_names'] = attribute_names
        request.session['filter_values'] = filter_values
        request.session['filter_names'] = filter_names

        return HttpResponseRedirect('/output')

    print('\nGot Data Selection Request\n')

    return render(request, 'datapipeline/dataSelection-2.html', context)

######################################
# Input: lodt - list of strings representing data category (table) names
# Returns: str - string for JOIN statement in a query
# Description: Helper function, not associated with a template
# Given a list of data category names, join them all together by subject_id
######################################
def make_join(lodt):
    str = ""
    str += "studygroup JOIN subject ON studygroup.study_group_id = subject.study_group_id JOIN "
    str += lodt[0] + " ON "+lodt[0]+".subject_id = subject.subject_id"
    if len(lodt) >= 2:
        str += " JOIN "+lodt[1]+" ON "+lodt[0] + \
            ".subject_id = "+lodt[1]+".subject_id"
    if len(lodt) == 3:
        str += " JOIN " + lodt[2] + " ON " + lodt[0] + \
            ".subject_id = " + lodt[2] + ".subject_id"
    return str

######################################
# Input: dictOfConds - dictionary of dictionary, inner dictionary has
# "name" and "value" of form fields from filter form.
# study_group_names - name of study groups selected for viewing
# Returns: str - string for JOIN statement in a query
# Description: Helper function, not associated with a template
# Given a list of data category names, join them all together by subject_id
######################################
def make_conds(dictOfConds, study_group_names):
    symbols = {
        'equal': '=',
        'notequal': '!=',
        'less': '<',
        'greater': '>',
        'lessorequal': '<=',
        'greaterorequal': '>='
    }
    if not dictOfConds:
        return None
    stry = ""
    first = True
    print()
    print(dictOfConds)
    print()
    for filter in dictOfConds:
        if first == True:
            if '_checkbox' in filter['name']:
                fixedName = filter['name'].replace('_checkbox', "")
                stry += fixedName
            elif '_dropdown' in filter['name']:
                stry += symbols[filter['value']]
            elif '_text' in filter['name']:
                stry += filter['value']
            first = False
        else:
            if '_checkbox' in filter['name']:
                fixedName = filter['name'].replace('_checkbox', "")
                stry += " AND "
                stry += fixedName
            elif '_dropdown' in filter['name']:
                stry += symbols[filter['value']]
            elif '_text' in filter['name']:
                properDataTypeVal = ViewHelper.returnProperType(filter['value'])
                stry += properDataTypeVal
    first = True
    for item in study_group_names:
        seperator = " ("
        stripped = item.split(seperator, 1)[0]
        if first == True:
            stry += " AND (StudyGroup.study_group_name = '"+stripped+"'"
            first = False
        else:
            stry += " OR StudyGroup.study_group_name = '"+stripped+"'"
    stry += ")"
    return stry

######################################
# Input: HTTPRequest
# Returns: HTTPResponse
# Description: Creates and writes a ".csv" of the selected data
######################################
def export_data(request):
    print('Exporting data')

    response = HttpResponse(content_type='text/csv')

    response['Content-Disposition'] = 'attachment; filename="study_data.csv"'

    #get the data
    result = DBClient.executeQuery(request.session['args'], 1)

    writer = csv.writer(response)
    #write the headers
    writer.writerow(request.session['attribute_names'])
    #each line in the query
    for row in result:
        writer.writerow(row)

    return response

######################################
# Input: HTTPRequest
# Returns: HTTPResponse
# Description: Creates and writes a ".csv" of the selected data's summary statistics
######################################
def export_summary(request):
    print('Exporting summary')

    response = HttpResponse(content_type='text/csv')

    # Set up stats summary
    engine = create_engine(settings.DB_CONNECTION_URL)
    df = pd.read_sql_query(sql=DBClient.buildQuery(request.session['args']), con=engine)
    stat_summary = df.describe().apply(lambda s: s.apply(lambda x: format(x, 'g')))

    #create the csv
    stat_summary.to_csv(path_or_buf=response)

    return response

######################################
# Input: HTTPRequest
# Returns: HTTPResponse
# Description: Executes final query and displays the selected data
# and the summary statistics of that data for template output.html
######################################
def output(request):

    #get all items from the session
    study_names = []
    if 'category_names' in request.session:
        study_names = request.session['study_names']

    category_names = []
    if 'category_names' in request.session:
        category_names = request.session['category_names']

    study_group_names = []
    if 'study_group_names' in request.session:
        study_group_names = request.session['study_group_names']

    attribute_names = []
    if 'attribute_names' in request.session:
        attribute_names = request.session['attribute_names']

    filter_values = []
    if 'filter_values' in request.session:
        filter_values = request.session['filter_values']
        
    #get arguments to create query in DBClient
    args = {
        'selectors': ', '.join(attribute_names),
        'from': make_join(category_names),
        'join-type': None,
        'join-stmt': None,
        'where': make_conds(filter_values, study_group_names),
        'group-by': None,
        'order-by': None
    }

    #get the data
    result = DBClient.executeQuery(args, 1)

    # Set up stats summary
    engine = create_engine(settings.DB_CONNECTION_URL)
    df = pd.read_sql_query(sql=DBClient.buildQuery(args), con=engine)

    #print(df.dtypes)
    correctType = False
    for datatype in df.dtypes:
        if datatype == np.int64 or datatype == np.float64:
            correctType = True
            break
    record_list = []
    if correctType == True:
        stat_summary = df.describe().apply(lambda s: s.apply(lambda x: format(x, 'g')))
        #print(stat_summary)
        header = ("",)
        for x in stat_summary.columns:
            header += (x,)
        records = stat_summary.to_records(index=True)
        #print(records)
        record_list = list(records)
        record_list.insert(0, header)
    #print(record_list)

    #saved to session for exporting
    request.session['args'] = args
    request.session['attribute-names'] = attribute_names

    context = {
        'data': result,
        "attribute_names": attribute_names,
        'stat_summary': record_list,
        'myCSS': 'output.css',
    }

    return render(request, 'datapipeline/output.html', context)
