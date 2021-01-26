from django.shortcuts import render
from django import forms
from django.shortcuts import HttpResponse
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect, HttpResponse
from django.core import serializers
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required

from datapipeline.views import home
from datapipeline.database import DBClient
from datapipeline.models import Study, StudyGroup, DataCategory, DataCategoryStudyXref

from .viewHelpers import Helper, DBFunctions
from . import views
from .forms import UploaderInfoForm, StudyNameForm, UploadInfoCreationForm, UploadPositionForm, StudyInfoForm, DisabledInputForm
from .tasks import ProcessUpload
from .uploaderinfo import UploaderInfo

import celery, jsonpickle
import json


# FIRST PAGE
@login_required
def study(request):
    context = {
         'myCSS': 'uploaderStudy.css',
    }
    
    #############################################################################################################
    if request.method == 'POST':
        studyNameForm = StudyNameForm(request.POST)
        fields = []
        
        if studyNameForm.is_valid():
            for field in studyNameForm.fields:
                if studyNameForm.cleaned_data[field]:
                    fields.append(
                        {
                            'name': field,
                            'value': studyNameForm[field].data
                        }
                    )
            studyName = fields[0].get('value')
            request.session['studyName'] = studyName
            request.session['checkedForDuplications'] = False
            
            studyExists = Study.objects.filter(study_name=studyName, owner=request.user.id).exists()
            
            if studyExists is False:
                return redirect(studyInfo)
            
            return redirect(info)
            
    #############################################################################################################           
    elif request.method == 'GET':
        
        Helper.clearKeyInSession(request.session, 'studyName')
        Helper.clearKeyInSession(request.session, 'uploaderInfo')
        Helper.clearKeyInSession(request.session, 'studyGroups')
        Helper.clearKeyInSession(request.session, 'dataCategories') 
        Helper.deleteAllDocuments()
        
        allStudies = Study.objects.filter(owner=request.user.id)
        
        studyNames = [ study.study_name for study in allStudies ]
            
        context['studies'] = studyNames
        
    #############################################################################################################
        
    form = StudyNameForm()
    
    context['form'] = form 
    
    return render(request, 'uploader/studyName.html', context)


# PAGE IF STUDY DOESN'T EXIST IN STUDY TABLE
@login_required
def studyInfo(request):
    
    if Helper.pathIsBroken(request.session, False):
        return redirect(study)
    
    
    studyName = request.session['studyName']
    
    context = {
         'myCSS': 'uploaderStudyInfo.css',
         'studyName': studyName,
         'error': False
    }
    
    context['form'] = StudyInfoForm()
    
    #############################################################################################################
    if request.method == 'POST':
        form = StudyInfoForm(request.POST)
        
        fields = {}
        
        if form.is_valid():
            for field in form.fields:
                if form.cleaned_data[field]:
                    fields[field] = form[field].data 
        
            studyDescription = fields.get('studyDescription')
            hasIRB = fields.get('isIRB_Approved')
            institutions = fields.get('institutions', '') 
            startDate = Helper.getDatetime(fields.get('startDate')) 
            endDate = Helper.getDatetime(fields.get('endDate')) 
            contactInfo = fields.get('contactInfo', '')
            visibility = fields.get('visibility', '')
            notes = fields.get('notes', '')
        
            # VERIFIES THAT STARTING DATE IS NOT AFTER ENDING DATE
            if Helper.validDates(startDate, endDate):
                newStudy = Study.objects.create(study_name=studyName,
                                                owner=request.user,
                                                study_description=studyDescription, 
                                                is_irb_approved=hasIRB, 
                                                institutions_involved=institutions, 
                                                study_start_date=startDate, 
                                                study_end_date=endDate, 
                                                study_contact=contactInfo,
                                                visibility=visibility,
                                                study_notes=notes)
            
                return redirect(info)
            
            else:
                context['form'] = form
                context['error'] = True
            
        #############################################################################################################
    
    return render(request, 'uploader/studyInfo.html', context)


# PAGE THAT GETS THE UPLOADED CSV FILES
@login_required
def info(request):
    
    if Helper.pathIsBroken(request.session):
        return redirect(study)
    
    studyName = request.session['studyName']
    checkedForDuplications = request.session['checkedForDuplications']
    
    context = {
         'myCSS': 'uploaderInfo.css',
         'studyName': studyName
    }
    
    studyID = (Study.objects.get(study_name=studyName, owner=request.user.id)).study_id
    #############################################################################################################
    if request.method == 'POST':
        uploaderForm = UploaderInfoForm(request.POST, request.FILES)
                
        if uploaderForm.is_valid():
            files = request.FILES.getlist('uploadedFiles')
            
            fields, filenames = Helper.getFieldsFromInfoForm(uploaderForm, files)
        
        
        uploaderInfo = UploaderInfo(studyName)
        uploaderInfo.studyID = studyID
        uploaderInfo.subjectOrganization = fields.get('subjectOrganization')
        rawTimeSeries = fields.get('isTimeSeries')
        uploaderInfo.isTimeSeries = True if rawTimeSeries == 'y' else False

        # If group name is a blank string, treat as default group
        if fields.get('groupName') is None:
            defaultGroup = True
            uploaderInfo.groupName = "(default)"
            print("Default group")
        else:
            defaultGroup = False
            uploaderInfo.groupName = fields.get('groupName')

        uploaderInfo.categoryName = Helper.cleanCategoryName(fields.get('categoryName'))
        uploaderInfo.handleDuplicate = fields.get('handleDuplicate', 'N/A')
        
        if uploaderInfo.handleDuplicate == 'N/A':
            checkedForDuplications = False 
        
        if checkedForDuplications is False or uploaderInfo.handleDuplicate == 'newFile':
            duplicateFiles = []
            for filename in filenames:
                if uploaderInfo.documentExists(filename):
                    duplicateFiles.append(filename)
                    
            if len(duplicateFiles) > 0:
                context['studyGroups'] = request.session['studyGroups']
                context['dataCategories'] = request.session['dataCategories']
                uploaderForm.fields['handleDuplicate'].required = True
                context['form'] = uploaderForm 
                
                Helper.deleteAllDocuments()
                dups = ', '.join(duplicateFiles)
                allFiles = ', '.join(filenames)
                messages.warning(request, f'Found Duplicates! Duplicate Files: {dups} || All Files Being Uploaded: {allFiles}')
                
                request.session['checkedForDuplications'] = True 
                return render(request, 'uploader/info.html', context)
        
        if 'handleDuplicate' not in fields:
            uploaderInfo.handleDuplicate = 'append'
            
        specialFlag = False
        specialRow = False
        
        if uploaderInfo.isTimeSeries and (uploaderInfo.subjectOrganization == 'row' or uploaderInfo.subjectOrganization == 'column'):
            if uploaderInfo.subjectOrganization == 'row':
                specialRow = True 
                
            specialFlag = True
        
        print('Special Flag', specialFlag)
        uploaderInfo.specialCase = specialFlag 

        # READING THE CSV FILE
        firstFile = filenames[0]
        path = 'uploaded_csvs/{}'.format(firstFile)
        
        if specialRow is False and Helper.hasAcceptableHeaders(path) is False:
            request.session['errorMessage'] = "No Headers Were Detected in the CSV File"
            uploaderInfo = {'filenames': filenames}
            request.session['uploaderInfo'] = jsonpickle.encode(uploaderInfo)
            return redirect(error)
        
        headers, hasSubjectNames, subjectPerCol = Helper.extractHeaders(path, uploaderInfo.subjectOrganization)
        
        uploaderInfo.headers = headers
        
        groupID = DBFunctions.getGroupID(uploaderInfo.groupName, studyID)

        # Set default description and insert study group here if using the default study group for the first time
        if groupID == -1 and defaultGroup:
            description = "This is the default study group if no study group is specified."
            DBFunctions.insertToStudyGroup(uploaderInfo.groupName, description, studyID)
        groupID = DBFunctions.getGroupID(uploaderInfo.groupName, studyID)
        
        data_category_id = DBFunctions.getDataCategoryIDIfExists(uploaderInfo.categoryName, uploaderInfo.isTimeSeries, uploaderInfo.subjectOrganization, studyID)
        
        if data_category_id != -1:
            uploaderInfo.updateFieldsFromDataCategory(data_category_id)
        
        uploaderInfo.groupID = groupID
        uploaderInfo.dcID = data_category_id
        uploaderInfo.subjectPerCol = subjectPerCol
        uploaderInfo.hasSubjectNames = hasSubjectNames
        uploaderInfo.uploadedFiles = filenames
        
        
        # ALLOWING FIELDS TO BE PASSED AROUND
        request.session['uploaderInfo'] = jsonpickle.encode(uploaderInfo)
        
        # CONDITIONS IF EXTRA INFORMATION IS NEEDED
        if (groupID == -1) or (data_category_id == -1):
            print('here')
            return redirect(extraInfo)
            
        else:
            return redirect(finalPrompt)
    
    #############################################################################################################
          
    elif request.method == 'GET':
        print('\nGot Uploader Info Request\n')
        request.session['checkedForDuplications'] = False
        Helper.deleteAllDocuments()
        groupsExist = StudyGroup.objects.filter(study=studyID)
        
        studyGroups = []
        
        if groupsExist:
            groupObjs = StudyGroup.objects.filter(study=studyID)
            
            studyGroups = [obj.study_group_name for obj in groupObjs]
            
        dataCategories = DBFunctions.getAllDataCategoriesOfStudy(studyID)
        
        context['studyGroups'] = studyGroups
        request.session['studyGroups'] = studyGroups
        context['dataCategories'] = dataCategories
        request.session['dataCategories'] = dataCategories
    
    #############################################################################################################
    
    form = UploaderInfoForm()
    form.fields['handleDuplicate'].widget = forms.HiddenInput()
    context['form'] = form
    
    return render(request, 'uploader/info.html', context)

@login_required
def extraInfo(request):
    
    if Helper.pathIsBroken(request.session, True):
        return redirect(study)
    
    studyName = request.session['studyName']
    uploaderInfo = jsonpickle.decode(request.session['uploaderInfo'])
    
    context = {
         'myCSS': 'uploaderExtraInfo.css',
         'studyName': studyName
    }
    
    headers = uploaderInfo.headers
    subjectRule = uploaderInfo.subjectOrganization
    isTimeSeries = uploaderInfo.isTimeSeries
    studyID = uploaderInfo.studyID
    groupID = uploaderInfo.groupID
    groupName = uploaderInfo.groupName
    dcID = uploaderInfo.dcID
    
    if uploaderInfo.specialCase:
        headers = ['Entered Name']
        
    form = UploadInfoCreationForm(None, dynamicFields=headers)
    
    ############################################################################################################# 
    if request.method == 'POST':
        form = UploadInfoCreationForm(request.POST, dynamicFields=headers)
        form.reset()
        
        myFields, myExtras = {}, []
        
        if form.is_valid():
            for (i, val) in form.getAllFields():
                myFields[i] = val 
            
            for (name, val) in form.getExtraFields():
                myExtras.append((name, val))
        
        if uploaderInfo.specialCase:
            colName = myFields.get('nameOfValueMeasured')
            dataType = myExtras[0][1]
            dataType = Helper.getActualDataType(dataType)
            uploaderInfo.specialInsert = { colName: {'position': '0', 'dataType': dataType} }
            myExtras = Helper.replaceWithNameOfValue(myExtras, colName)
            
        if subjectRule == 'column':
            myFields['hasSubjectID'] = 'y'
            

        if groupID == -1:
            description = myFields.get('studyGroupDescription')
            
            DBFunctions.insertToStudyGroup(groupName, description, studyID)
            
            groupID = DBFunctions.getGroupID(groupName, studyID)
            
            uploaderInfo.groupID = groupID


        if dcID == -1:
            errorMessage = uploaderInfo.handleMissingDataCategoryID(subjectRule, [myFields, myExtras])
            
            if errorMessage is not None:
                request.session['errorMessage'] = errorMessage + " Please review the guidelines carefully and make sure your files follow them."
                return redirect(error)
        
        if uploaderInfo.subjectPerCol is True:
            uploaderInfo.hasSubjectNames = True
        
        request.session['uploaderInfo'] = jsonpickle.encode(uploaderInfo)
        
        return redirect(finalPrompt)
    
    #############################################################################################################     
    elif request.method == 'GET':
        case1 = False
        if uploaderInfo.specialCase:
            print('FOUND CASE 1')
            form.fields['nameOfValueMeasured'].required = True
            
            context['case1'] = True
            if subjectRule == 'column':
                form.fields['hasSubjectID'].required = False
                context['withSubjectID'] = False
            
            else:
                context['withSubjectID'] = True


        if groupID == -1:
            print('FOUND CASE 2')
            form.fields['studyGroupDescription'].required = True 
            context['case2'] = True 

        if dcID == -1:
            print('FOUND CASE 3')
            form.fields['dataCategoryDescription'].required = True
            context['case3'] = True

                 
        print('\nGot Uploader Extra Info Request\n')
        
    #############################################################################################################
        
    context['form'] = form
    
    return render(request, 'uploader/extraInfo.html', context)


@login_required
def finalPrompt(request):
    
    if Helper.pathIsBroken(request.session, True):
        return redirect(study)
    
    studyName = request.session['studyName']
    uploaderInfo = jsonpickle.decode(request.session['uploaderInfo'])
    
    context = {
         'myCSS': 'uploaderFinalPrompt.css',
         'myJS': 'uploaderFinalPrompt.js',
         'studyName': studyName,
         'error': False
    }
    
    headers = uploaderInfo.headers
    isTimeSeries = uploaderInfo.isTimeSeries
    subjectOrg = uploaderInfo.subjectOrganization
    tableName = uploaderInfo.tableName
    dcID = uploaderInfo.dcID
    
    form = UploadPositionForm(None, columns=headers)
    context['form'] = form
    #############################################################################################################
    if request.method == 'POST':
        form = UploadPositionForm(request.POST, columns=headers)
        myFields = []
        
        if form.is_valid():
            for (i, val) in form.getColumnFields():
                myFields.append((i, val)) 
        
        clean = Helper.seperateByName(myFields, 2, True)       
        
        if Helper.foundDuplicatePositions(clean) is True:
            context['error'] = True
            context['form'] = form
            
        else:
            request.session['positionInfo'] = clean 
            
            return redirect(upload)
            
    #############################################################################################################
    elif request.method == 'GET':
        if uploaderInfo.specialCase:
            colName, dataType = DBFunctions.getAttributeOfTable(tableName)
            uploaderInfo.specialInsert = { colName: {'position': '0', 'dataType': dataType} }
            request.session['uploaderInfo'] = jsonpickle.encode(uploaderInfo)
            
            return redirect(upload)
        
    #############################################################################################################
    
    tableSchema = DBFunctions.getTableSchema(tableName, dcID)
    
    context['schema'] = tableSchema
    
    
    return render(request, 'uploader/finalPrompt.html', context)

@login_required
def upload(request):
    
    if Helper.pathIsBroken(request.session):
        return redirect(study)
    
    studyName = request.session['studyName']
    positionInfo = request.session['positionInfo']
    uploaderInfo = jsonpickle.decode(request.session['uploaderInfo'])
    
    filenames = uploaderInfo.uploadedFiles
    hasSubjectNames = uploaderInfo.hasSubjectNames

    form = DisabledInputForm()
    
    context = {
         'myCSS': 'uploader.css',
         'studyName': studyName,
         'form': form,
    }
    
    if request.is_ajax() and request.method == 'POST':

        status = request.POST['status']
        message = request.POST['message']
        
        if status == 'FAILED':
            request.session['errorMessage'] = message + " Please review the guidelines carefully and make sure you did not make any mistakes during the uploader process."
            return HttpResponse(status=400)
        
        else:
            return HttpResponse(status=200)
        
        
    elif request.method == 'POST':
        
        specialFlag = False 

        if uploaderInfo.specialInsert != '':
            positionInfo = uploaderInfo.specialInsert
            specialFlag = True

        task = ProcessUpload.delay(filenames, jsonpickle.encode(uploaderInfo), positionInfo, specialFlag)
        
        print (f'Celery Task ID: {task.task_id}')
            
        context['task_id'] = task.task_id
        
        return render(request, 'uploader/progress.html', context)
    
    elif request.method == 'GET':
        files_to_be_uploaded = "Files to be uploaded: "
        
        for file in filenames:
            files_to_be_uploaded += f"{file} "
    
        form.fields['files'].widget.attrs['placeholder'] = files_to_be_uploaded
    
        context['form'] = form
        

        
    return render(request, 'uploader/uploading.html', context) 

@login_required
def error(request):
    context = {
         'myCSS': 'uploaderError.css'
    }
    
    
    if request.method == 'POST':
        Helper.clearKeyInSession(request.session, 'uploaderInfo') 
        Helper.clearKeyInSession(request.session, 'studyGroups')
        Helper.clearKeyInSession(request.session, 'dataCategories')  

        Helper.deleteAllDocuments()
        return redirect(home)
    
    elif request.method == 'GET':
        if request.session.get('errorMessage', None) != None:
            context['errorMessage'] = request.session['errorMessage']
            
        if request.session.get('uploaderInfo', None) != None:
            uploaderInfo = jsonpickle.decode(request.session['uploaderInfo'])
            filenames = uploaderInfo.uploadedFiles

            uploaded, notUploaded = Helper.getUploadResults(filenames)
            
            context['uploaded'] = uploaded 
            context['notUploaded'] = notUploaded
            
        
    return render(request, 'uploader/errorPage.html', context) 

@login_required
def success(request):
    context = {
         'myCSS': 'uploaderSuccess.css'
    }
    
    if request.method == 'POST':
        if 'finished' in request.POST:
            Helper.clearKeyInSession(request.session, 'studyName')
            return redirect(home)
        
        elif 'continue' in request.POST:
            Helper.clearKeyInSession(request.session, 'uploaderInfo') 
            Helper.clearKeyInSession(request.session, 'studyGroups')
            Helper.clearKeyInSession(request.session, 'dataCategories') 
            
            return redirect(info)
        
    elif request.method == 'GET':
        if request.session.get('uploaderInfo', None) != None:
            uploaderInfo = jsonpickle.decode(request.session['uploaderInfo'])
            filenames = uploaderInfo.uploadedFiles

            uploaded, notUploaded = Helper.getUploadResults(filenames)
            
            context['uploaded'] = uploaded 
            context['notUploaded'] = notUploaded
        
    
    return render(request, 'uploader/successPage.html', context) 
