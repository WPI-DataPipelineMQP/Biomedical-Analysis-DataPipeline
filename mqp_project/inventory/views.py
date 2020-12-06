from django.http import HttpResponseRedirect
from django.shortcuts import render
from datapipeline.database import DBClient, DBHandler
from datapipeline.forms import CreateChosenBooleanForm
from datapipeline.viewHelpers import viewsHelper as ViewHelper

# 1st screen: Show list of studies and allow user to start selection on them or use links to study page
def listStudies(request):
    study_fields = []
    study_ids = {}
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
        study_ids[study_name] = study_id

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

        data_categories = DBHandler.getDataCategoriesOfStudies(study_ids_forquery)

        study_groups = DBHandler.getStudyGroupsOfStudies(study_ids_forquery)

        # gets the names to be printed out
        study_names = ViewHelper.getNameList(studies_data, True)

        request.session['study_names'] = study_names
        request.session[
            'studies_data'] = studies_data  # NOTE: after this edit, do we still need this in the session?
        request.session['data_categories'] = data_categories
        request.session['study_groups'] = study_groups

        return HttpResponseRedirect('/dataSelection')
        # return render(request, 'datapipeline/studySelection.html', context)

    studies_form = CreateChosenBooleanForm(customFields=study_fields)

    context = {
        'studies_form': studies_form,
        'study_ids': study_ids,
        'myCSS': 'studySelection.css'
    }
    return render(request, 'inventory/listStudies.html', context)

# 2nd Screen: Show metadata on study, study groups, data categories, attributes
def studySummary(request, id):

    study_dict = getStudy(id)
    if not study_dict:
        return render(request, 'inventory/error.html', {'error': 'Study with ID {} not found!'.format(id)})

    studygroups_dict = getStudyGroups(id)
    data_category_dict = getDataCategories(id)

    study_dict['total_groups'] = len(studygroups_dict)
    study_dict['total_data_categories'] = len(data_category_dict)

    context = {
        'study': study_dict,
        'studygroups': studygroups_dict,
        'datacategories': data_category_dict
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
            'from': 'Subject Join Demographics on Subject.subject_id = Demographics.subject_id ',
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
            'from': 'Subject Join Demographics on Subject.subject_id = Demographics.subject_id ',
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