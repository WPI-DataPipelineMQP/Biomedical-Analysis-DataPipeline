from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from datapipeline.database import DBClient, DBHandler
from datapipeline.forms import CreateChosenBooleanForm
from datapipeline.viewHelpers import viewsHelper as ViewHelper
from uploader.viewHelpers import Helper as UploadHelper
from uploader.viewHelpers import DBFunctions
from .forms import DataCategorySearchForm
from django.contrib import messages
from django.db.models import Q
from datapipeline.models import Study
from django.contrib.auth.models import User
from django.db.models.base import ObjectDoesNotExist

# 1st screen: Show list of studies and allow user to start selection on them or use links to study page
def listStudies(request):
    UploadHelper.deleteAllDocuments()
    dc_searchTerm = None

    # If submit button was clicked to go to selection
    if request.method == 'POST' and 'selection-btn' in request.POST:
        study_fields = request.session['study_fields']

        studies_form = CreateChosenBooleanForm(request.POST, customFields=study_fields)

        studies_data = {}

        if studies_form.is_valid():
            for i, field in enumerate(studies_form.getAllFields()):
                studies_data[i] = {
                    'name': study_fields[i]['name'],
                    'value': field[1],
                    'id': study_fields[i]["id"]
                }

        study_ids_forquery = ''

        # MAKING THE QUERY TO USE
        for i, key in enumerate(studies_data):
            study = studies_data[key]

            if study.get('value') is True:
                if study_ids_forquery != '':
                    study_ids_forquery += 'OR '

                if i == (len(studies_data) - 1):
                    study_ids_forquery += 'study_id = {}'.format(study['id'])

                else:
                    study_ids_forquery += 'study_id = {} '.format(study['id'])

        if study_ids_forquery == '':
            messages.error(request, 'Please select at least one study to start selection analysis')
            return redirect('inventory-listStudies')

        data_categories = DBHandler.getDataCategoriesOfStudies(study_ids_forquery)

        study_groups = DBHandler.getStudyGroupsOfStudies(study_ids_forquery)

        # gets the names to be printed out
        study_names = ViewHelper.getNameList(studies_data, True)

        request.session['study_names'] = study_names
        request.session[
            'studies_data'] = studies_data  # NOTE: after this edit, do we still need this in the session?
        request.session['data_categories'] = data_categories
        request.session['study_groups'] = study_groups

        return redirect('datapipeline-dataSelection')

    # if searching for studies with a data category
    elif request.method == 'POST' and 'searchTerm' in request.POST:
        dc_search_form = DataCategorySearchForm(request.POST)
        dc_searchTerm = ""
        if dc_search_form.is_valid():
            dc_searchTerm = dc_search_form.cleaned_data['searchTerm']

        # If search term is blank, reset search
        if dc_searchTerm == "":
            return redirect('inventory-listStudies')

    # Get request
    study_fields = []
    study_ids = []
    studies = Study.objects.filter(
            ~(Q(visibility="Private") & ~Q(owner=request.user.id))
        )

    # If using a search term, query for specific studies that contain a data category with a name similar to the search term
    if dc_searchTerm is not None:
        studiesWithDc = set() # Uses a set instead of list to prevent duplicate studies listed
        for study in studies:
            dcs = DBFunctions.getAllDataCategoriesOfStudy(study.study_id)
            for dc in dcs:
                if dc_searchTerm in dc:
                    studiesWithDc.add(study)
                    break
        studies = studiesWithDc

    for study in studies:
        studies_dict = {}
        studies_dict["name"] = study.study_name
        studies_dict["description"] = study.study_description
        studies_dict["id"] = study.study_id
        study_fields.append(studies_dict)
        study_ids.append(study.study_id)
    request.session['study_fields'] = study_fields


    studies_form = CreateChosenBooleanForm(customFields=study_fields)

    # Fill in search bar with search term if searching
    if dc_searchTerm is None:
        dc_search_form = DataCategorySearchForm()
    else:
        dc_search_form = DataCategorySearchForm(request.POST)

    context = {
        'studies_form': studies_form,
        'dc_search_form': dc_search_form,
        'study_ids': study_ids,
        'myCSS': 'inventoryListStudies.css'
    }
    return render(request, 'inventory/listStudies.html', context)

# 2nd Screen: Show metadata on study, study groups, data categories, attributes
def studySummary(request, id):

    study_dict = getStudy(id)
    if not study_dict:
        return render(request, 'inventory/error.html', {'error': 'Study with ID {} not found!'.format(id)})

    if not Study.objects.filter(~(Q(visibility="Private") & ~Q(owner=request.user.id)), study_id=id):
        return render(request, 'inventory/error.html', {'error': 'You do not have permission to view this study!'.format(id)})

    studygroups_dict = getStudyGroups(id)
    data_category_dict = getDataCategories(id)

    study_dict['total_groups'] = len(studygroups_dict)
    study_dict['total_data_categories'] = len(data_category_dict)

    context = {
        'study': study_dict,
        'studygroups': studygroups_dict,
        'datacategories': data_category_dict,
        'myCSS': 'inventoryStudy.css'
    }
    return render(request, 'inventory/study.html', context)


# Gets study metadata given a study_id
def getStudy(id):
    args = {
        'selectors': '*',
        'from': 'Study',
        'join-type': None,
        'join-stmt': None,
        'where': 'study_id = '+id,
        'group-by': None,
        'order-by': None
    }
    result = DBClient.executeQuery(args,0)

    # Could not find study with id from url
    if not result:
        return None

    study = result[0]

    study_dict = {}
    study_dict['name'] = study[1]
    study_dict['description'] = study[2]
    study_dict['irb'] = 'Approved' if study[3] else 'Unapproved'
    study_dict['inst'] = study[4]
    study_dict['start'] = study[5]
    study_dict['end'] = study[6]
    study_dict['contact'] = study[7]
    study_dict['notes'] = study[8]
    study_dict['total_subjects'] = len(getStudySubjects(id))
    try:
        owner = User.objects.get(pk=study[9])
    except ObjectDoesNotExist:
        owner = "None"
    study_dict['owner'] = owner
    study_dict['visibility'] = study[10]

    return study_dict

# Gets meta data for each study group
def getStudyGroups(study):
    args = {
        'selectors': '*',
        'from': 'StudyGroup',
        'join-type': None,
        'join-stmt': None,
        'where': 'study_id = '+study,
        'group-by': None,
        'order-by': None
    }
    result = DBClient.executeQuery(args,0)

    study_groups = []
    for study_group in result:
        study_group_dict = {}
        study_group_dict['name'] = study_group[1]
        study_group_dict['description'] = study_group[2]
        study_group_dict['total_subjects'] = len(getStudyGroupSubjects(study_group[0]))
        study_groups.append(study_group_dict)

    return study_groups

def getStudySubjects(study):
    args = {
            'selectors': '*',
            'from': 'Subject',
            'join-type': 'Join',
            'join-stmt': 'StudyGroup on Subject.study_group_id = StudyGroup.study_group_id WHERE StudyGroup.study_id = ' + study,
            'where': None,
            'group-by': None,
            'order-by': 'StudyGroup.study_group_name, Subject.subject_id'
    }
    result = DBClient.executeQuery(args, 0)
    return result

def getStudyGroupSubjects(study_group):
    args = {
            'selectors': '*',
            'from': 'Subject',
            'join-type': 'Join',
            'join-stmt': 'StudyGroup on Subject.study_group_id = StudyGroup.study_group_id WHERE StudyGroup.study_group_id = ' + str(study_group),
            'where': None,
            'group-by': None,
            'order-by': 'StudyGroup.study_group_name, Subject.subject_id'
    }
    result = DBClient.executeQuery(args, 0)
    return result


# Get metadata for each data category
def getDataCategories(study):
    args = {
        'selectors': 'data_category_name, is_time_series, DataCategory.dc_table_name, DataCategory.dc_description, DataCategory.data_category_id',
        'from': 'DataCategory',
        'join-type': 'JOIN',
        'join-stmt': 'DataCategoryStudyXref ON DataCategory.data_category_id = DataCategoryStudyXref.data_category_id WHERE study_id = ' + study,
        'where': None,
        'group-by': None,
        'order-by': None
    }
    result = DBClient.executeQuery(args,0)

    data_categories = []
    for data_category in result:
        data_category_dict = {}
        data_category_dict['name'] = data_category[0]
        data_category_dict['total_records'] = getNumberOfDataRecords(study, data_category[2])
        data_category_dict['time_series'] = 'True' if data_category[1] else 'False'
        data_category_dict['description'] = data_category[3]
        data_category_dict['attributes'] = getAttributes(data_category[4])
        data_category_dict['total_attributes'] = len(data_category_dict['attributes'])
        data_categories.append(data_category_dict)

    return data_categories

# Query number of records in a data table which belongs to a given study
def getNumberOfDataRecords(study, data_category):
    args = {
        'selectors': '*',
        'from': data_category,
        'join-type': 'JOIN',
        'join-stmt': 'Subject on Subject.subject_id =' + data_category + '.subject_id' +
        ' Join StudyGroup on Subject.study_group_id = StudyGroup.study_group_id ' +
            'where StudyGroup.study_id =' + study,
        'where': None,
        'group-by': None,
        'order-by': None
    }
    result = DBClient.executeQuery(args, 0)
    return "{:,}".format(len(result))

def getAttributes(data_category):
    args = {
        'selectors': 'attr_name, attr_description, data_type, unit, device_name',
        'from': 'Attribute',
        'join-type': None,
        'join-stmt': None,
        'where': "data_category_id=" + str(data_category),
        'group-by': None,
        'order-by': None
    }

    result = DBClient.executeQuery(args, 0)

    attributes = []

    for attribute in result:
        attribute_dict = {}
        attribute_dict['name'] = attribute[0]
        attribute_dict['attr_description'] = attribute[1]
        attribute_dict['data_type'] = getFormattedDataType(attribute[2])
        attribute_dict['unit'] = attribute[3]
        attribute_dict['device_name'] = attribute[4]
        attributes.append(attribute_dict)

    return attributes

# Convert attribute.data_type to a presentable type for user
def getFormattedDataType(dt):
    if 'VARCHAR' in dt or 'TEXT' in dt:
        return 'Text'
    elif dt == 'DATE':
        return 'Date'
    elif dt == 'TIME':
        return 'Time'
    elif dt == 'DATETIME':
        return 'Datetime'
    elif dt == 'INT':
        return 'Integer'
    elif dt == 'FLOAT':
        return 'Decimal'
    else:
        return dt