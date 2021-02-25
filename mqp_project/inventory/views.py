from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from datapipeline.database import DBClient, DBHandler
from datapipeline.forms import CreateChosenBooleanForm
from datapipeline.viewHelpers import viewsHelper as ViewHelper
from uploader.viewHelpers import Helper as UploadHelper
from uploader.viewHelpers import DBFunctions
from .forms import StudySearchForm
from django.contrib import messages
from django.db.models import Q
from datapipeline.models import Study, Subject, StudyGroup, DataCategoryStudyXref, Attribute
from django.contrib.auth.models import User
from django.db.models.base import ObjectDoesNotExist

######################################
# Input: HTTPRequest
# Returns: HTTPResponse
# Description: Lists studies on template listStudies.html
#  and allows user to search by metadata and use links to go to specific study pages
# NOTE: This page was built off of the studySelection page in datapipeline directory with
# the aim that users would be also able to go right into the selection process from this page as well.
# The button and checkboxes for this functionality were taken out very late into development due
# to frequent user confusion but the back end code is left over just in case.
######################################
def listStudies(request):
    UploadHelper.deleteAllDocuments()
    searchTerm = None

    # If submit button was clicked to go to selection. Everything within this if statement is currently unused
    if request.method == 'POST' and 'selection-btn' in request.POST:

        # save dictionary of studies to the session
        study_fields = request.session['study_fields']

        # create the dynamic form
        studies_form = CreateChosenBooleanForm(request.POST, customFields=study_fields)

        # gather the data from the form
        studies_data = {}
        if studies_form.is_valid():
            for i, field in enumerate(studies_form.getAllFields()):
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

        if study_ids_forquery == '':
            messages.error(request, 'Please select at least one study to start selection analysis')
            return redirect('inventory-listStudies')

        data_categories = DBHandler.getDataCategoriesOfStudies(study_ids_forquery)

        study_groups = DBHandler.getStudyGroupsOfStudies(study_ids_forquery)

        # gets the names to be printed out
        study_names = ViewHelper.getNameList(studies_data, True)

        request.session['study_names'] = study_names
        request.session['data_categories'] = data_categories
        request.session['study_groups'] = study_groups

        return redirect('datapipeline-dataSelection')

    # if searching for studies with specific metadata
    elif request.method == 'POST' and 'searchTerm' in request.POST:
        search_form = StudySearchForm(request.POST)
        searchTerm = ""
        if search_form.is_valid():
            searchTerm = search_form.cleaned_data['searchTerm'].lower() # Make lower case to remove case sensitivity
            searchStudyName = search_form.cleaned_data['studyName']
            searchStudyDescription = search_form.cleaned_data['studyDescription']
            searchInstitutionsInvolved = search_form.cleaned_data['institutionsInvolved']
            searchStudyContact = search_form.cleaned_data['studyContact']
            searchStudyNotes = search_form.cleaned_data['studyNotes']
            searchDataCategory = search_form.cleaned_data['dataCategory']

        # If search term is blank, reset search and refresh page
        if searchTerm == "":
            return redirect('inventory-listStudies')

        # If no checkboxes were selected, show error
        if any([searchStudyName, searchStudyDescription, searchInstitutionsInvolved, searchStudyContact,
                searchStudyNotes, searchDataCategory]) is False:
            messages.error(request, 'If you are searching, please select at least one type of metadata to search for.')
            return redirect('inventory-listStudies')

    # Get request
    study_fields = [] # Dictionary of study name, description and, id used in selection form
    study_ids = [] # Parallel list of study ids for each study, used for creating links to study pages

    # Get list of studies available to user, based on permissions
    studies = Study.objects.filter(
            ~(Q(visibility="Private") & ~Q(owner=request.user.id))
        )

    # If using a search term, query for specific studies with metadata that contains the search term
    if searchTerm is not None:
        matchingStudies = set() # Uses a set instead of list to prevent duplicate studies listed

        # Search visible studies for ones that contain the search term within the selected metadata
        for study in studies:

            # For each meta data field, check if the checkbox was selected, the study's field is not null
            # and the search term is within the study's field (after making lower case to remove case sensitivity)
            if searchStudyName and study.study_name and searchTerm in study.study_name.lower():
                matchingStudies.add(study)
            elif searchStudyDescription and study.study_description and searchTerm in study.study_description.lower():
                matchingStudies.add(study)
            elif searchInstitutionsInvolved and study.institutions_involved and searchTerm in study.institutions_involved.lower():
                matchingStudies.add(study)
            elif searchStudyContact and study.study_contact and searchTerm in study.study_contact.lower():
                matchingStudies.add(study)
            elif searchStudyNotes and study.study_notes and searchTerm in study.study_notes.lower():
                matchingStudies.add(study)
            elif searchDataCategory:
                dcs = DBFunctions.getAllDataCategoriesOfStudy(study.study_id)
                for dc in dcs:
                    if searchTerm in dc.lower():
                        matchingStudies.add(study)
                        break
        studies = matchingStudies

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
    if searchTerm is None:
        search_form = StudySearchForm()
    else:
        search_form = StudySearchForm(request.POST)

    context = {
        'studies_form': studies_form,
        'search_form': search_form,
        'study_ids': study_ids,
        'myCSS': 'inventoryListStudies.css'
    }
    return render(request, 'inventory/listStudies.html', context)

######################################
# Input: HTTPRequest
# id - study id of study you want to view. This will be in the url
# Returns: HTTPResponse
# Description: Lists metadata on a given study on template study.html
# # including its study groups, data categories, and attributes
# If the study cannot be viewed or does not exist, it displays an error on template error.html
######################################
def studySummary(request, id):

    # Display error page if study with given id does not exist
    try:
        study = Study.objects.get(pk=id)
    except ObjectDoesNotExist:
        return render(request, 'inventory/error.html', {'error': 'Study not found!'})

    # Check permission on study and display error if study is private and not owned by logged in user
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

######################################
# Input: study - study model object
# data_category - name of data category table
# Returns: Total number of rows of data within a data category that belongs to a specific study
# Description: Query number of records in a data table which belongs to a given study.
# This uses a raw sql query since the data categories use dynamically created tables which cannot be mapped to
# to Django models.
######################################
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

######################################
# Input: dt - string SQL data type of an attribute (attribute.data_type)
# Returns: string of formatted data type
# Description: Given a SQL data type, converts it to a more presentable data type for the user
######################################
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