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
from datapipeline.models import Study, Subject, StudyGroup, DataCategoryStudyXref, Attribute
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
    try:
        study = Study.objects.get(pk=id)
    except ObjectDoesNotExist:
        return render(request, 'inventory/error.html', {'error': 'Study not found!'})

    # Check permission on study
    if not Study.objects.filter(~(Q(visibility="Private") & ~Q(owner=request.user.id)), study_id=id):
        return render(request, 'inventory/error.html', {'error': 'You do not have permission to view this study!'.format(id)})

    # Additional study fields/formatting
    study.irb = 'Approved' if study.is_irb_approved else 'Unapproved'
    study.total_subjects = Subject.objects.filter(study_group__study=study).count()

    # Query study groups in study
    study_groups = list(StudyGroup.objects.filter(study=study).values()) # Properties cannot be added to querysets so the query results are forced into a list
    for study_group in study_groups:
        study_group['total_subjects'] = Subject.objects.filter(study_group=study_group['study_group_id']).count()

    study.total_groups = len(study_groups)

    # Query data categories in study group
    studysDCXrefs = DataCategoryStudyXref.objects.filter(study=study)

    data_categories = []
    for dcXref in studysDCXrefs:
        data_category = dcXref.data_category
        data_category.time_series = 'True' if data_category.is_time_series else 'False'
        data_category.total_records = getNumberOfDataRecords(study, data_category.dc_table_name)
        data_category.attributes = list(Attribute.objects.filter(data_category=data_category).values())
        data_category.total_attributes = len(data_category.attributes)

        for attr in data_category.attributes:
            attr['data_type'] = getFormattedDataType(attr['data_type'])

        data_categories.append(data_category)

    study.total_data_categories = len(data_categories)

    context = {
        'study': study,
        'studygroups': study_groups,
        'datacategories': data_categories,
        'myCSS': 'inventoryStudy.css'
    }
    return render(request, 'inventory/study.html', context)

# Query number of records in a data table which belongs to a given study. Needs to use raw sql due to use of dynamic tables
def getNumberOfDataRecords(study, data_category):
    args = {
        'selectors': '*',
        'from': data_category,
        'join-type': 'JOIN',
        'join-stmt': 'Subject on Subject.subject_id =' + data_category + '.subject_id' +
        ' Join StudyGroup on Subject.study_group_id = StudyGroup.study_group_id ' +
            'where StudyGroup.study_id =' + str(study.study_id),
        'where': None,
        'group-by': None,
        'order-by': None
    }
    result = DBClient.executeQuery(args, 0)
    return "{:,}".format(len(result))

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