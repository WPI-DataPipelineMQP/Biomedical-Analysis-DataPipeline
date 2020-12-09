from django.shortcuts import render
from django import forms
from django.shortcuts import HttpResponse
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect, HttpResponse
from django.core import serializers
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage

from datapipeline.views import home
from datapipeline.database import DBClient
from datapipeline.models import Study, StudyGroup, DataCategory, DataCategoryStudyXref

from .viewHelpers import Helper, DBFunctions, Handler
from . import views
from .forms import UploaderInfoForm, StudyNameForm, UploadInfoCreationForm, UploadPositionForm, StudyInfoForm, DisabledInputForm
from .tasks import ProcessUpload

import celery
import json


# FIRST PAGE
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
            
            studyExists = Study.objects.filter(study_name=studyName).exists()
            
            if studyExists is False:
                return redirect(studyInfo)
            
            return redirect(info)
            
    #############################################################################################################           
    elif request.method == 'GET':
        
        Helper.clearStudyName(request.session)
        Helper.clearUploadInfo(request.session)
        Helper.deleteAllDocuments()
        
        allStudies = Study.objects.all()
        
        studyNames = [ study.study_name for study in allStudies ]
            
        context['studies'] = studyNames
        
    #############################################################################################################
        
    form = StudyNameForm()
    
    context['form'] = form 
    
    return render(request, 'uploader/studyName.html', context)


# PAGE IF STUDY DOESN'T EXIST IN STUDY TABLE
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
            notes = fields.get('notes', '')
        
            # VERIFIES THAT STARTING DATE IS NOT AFTER ENDING DATE
            if Helper.validDates(startDate, endDate):
                newStudy = Study.objects.create(study_name=studyName, 
                                                study_description=studyDescription, 
                                                is_irb_approved=hasIRB, 
                                                institutions_involved=institutions, 
                                                study_start_date=startDate, 
                                                study_end_date=endDate, 
                                                study_contact=contactInfo, 
                                                study_notes=notes)
            
                return redirect(info)
            
            else:
                context['form'] = form
                context['error'] = True
            
        #############################################################################################################
    
    return render(request, 'uploader/studyInfo.html', context)


# PAGE THAT GETS THE UPLOADED CSV FILES
def info(request):
    
    if Helper.pathIsBroken(request.session):
        return redirect(study)
    
    studyName = request.session['studyName']
    checkedForDuplications = request.session['checkedForDuplications']
    
    context = {
         'myCSS': 'uploaderInfo.css',
         'studyName': studyName
    }
    
    studyID = (Study.objects.get(study_name=studyName)).study_id
    #############################################################################################################
    if request.method == 'POST':
        uploaderForm = UploaderInfoForm(request.POST, request.FILES)
                
        if uploaderForm.is_valid():
            files = request.FILES.getlist('uploadedFiles')
            
            fields, filenames = Helper.getFieldsFromInfoForm(uploaderForm, files)
        
                
        subjectOrgVal = fields.get('subjectOrganization')
        rawTimeSeries = fields.get('isTimeSeries')
        fields['isTimeSeries'] = True if rawTimeSeries == 'y' else False
        groupName = fields.get('groupName') 
        dataCategoryName = fields.get('categoryName')
        
        print(fields)
        if checkedForDuplications is False or fields.get('handleDuplicate', 'N/A') == 'newFile':
            duplicateFiles = []
            for filename in filenames:
                if Handler.documentExists(filename, dataCategoryName, fields['isTimeSeries'], studyID):
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
            fields['handleDuplicate'] = 'append'
            
        specialFlag = False
        specialRow = False
        
        if fields.get('isTimeSeries') and (subjectOrgVal == 'row' or subjectOrgVal == 'column'):
            if subjectOrgVal == 'row':
                specialRow = True 
                
            specialFlag = True 
            
        fields['SpecialCase'] = specialFlag
        
        # READING THE CSV FILE
        firstFile = filenames[0]
        path = 'uploaded_csvs/{}'.format(firstFile)
        
        if specialRow is False and Helper.hasAcceptableHeaders(path) is False:
            request.session['errorMessage'] = "No Headers Were Detected in the CSV File"
            uploaderInfo = {'filenames': filenames}
            request.session['uploaderInfo'] = uploaderInfo
            return redirect(error)
        
        headers, hasSubjectNames, subjectPerCol = Helper.extractHeaders(path, subjectOrgVal)
            
        fields['headerInfo'] = headers
        
        groupID = DBFunctions.getGroupID(groupName, studyID)
        
        data_category_id = DBFunctions.getDataCategoryIDIfExists(dataCategoryName, fields.get('isTimeSeries'), studyID)
        
        if data_category_id != -1:
            fields = Handler.updateFieldsFromDataCategory(data_category_id, fields)
            
        # UPDATING THE FIELDS
        fields['studyID'] = studyID
        fields['filenames'] = filenames
        fields['studyName'] = studyName
        fields['groupName'] = groupName
        fields['groupID'] = groupID
        fields['dcID'] = data_category_id
        fields['hasSubjectNames'] = hasSubjectNames 
        fields['subjectPerCol'] = subjectPerCol
        
        
        # ALLOWING FIELDS TO BE PASSED AROUND
        request.session['uploaderInfo'] = fields 
        
        # CONDITIONS IF EXTRA INFORMATION IS NEEDED
        if (groupID == -1) or (data_category_id == -1):

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


def extraInfo(request):
    
    if Helper.pathIsBroken(request.session, True):
        return redirect(study)
    
    studyName = request.session['studyName']
    uploaderInfo = request.session['uploaderInfo']
    
    context = {
         'myCSS': 'uploaderExtraInfo.css',
         'studyName': studyName
    }
    
    headers = uploaderInfo.get('headerInfo')
    subjectRule = uploaderInfo.get('subjectOrganization')
    isTimeSeries = uploaderInfo.get('isTimeSeries')
    studyID = uploaderInfo.get('studyID')
    groupID = uploaderInfo.get('groupID')
    groupName = uploaderInfo.get('groupName')
    dcID = uploaderInfo.get('dcID')
    
    if Helper.checkForSpecialCase(request.session):
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
        
        if Helper.checkForSpecialCase(request.session):
            colName = myFields.get('nameOfValueMeasured')
            dataType = myExtras[0][1]
            dataType = Helper.getActualDataType(dataType)
            uploaderInfo['specialInsert'] = { colName: {'position': '0', 'dataType': dataType} }
            myExtras = Helper.replaceWithNameOfValue(myExtras, colName)
            
        if subjectRule == 'column':
            myFields['hasSubjectID'] = 'y'
            

        if groupID == -1:
            description = myFields.get('studyGroupDescription')
            
            DBFunctions.insertToStudyGroup(groupName, description, studyID)
            
            groupID = DBFunctions.getGroupID(groupName, studyID)
            
            uploaderInfo['groupID'] = groupID
            
            
        if dcID == -1:
            uploaderInfo, errorMessage = Handler.handleMissingDataCategoryID(studyID, subjectRule, isTimeSeries, uploaderInfo, [myFields, myExtras])
            
            if errorMessage is not None:
                request.session['errorMessage'] = errorMessage + " Please review the guidelines carefully and make sure your files follow them."
                return redirect(error)
        
        if uploaderInfo.get('subjectPerCol') is True:
            uploaderInfo['hasSubjectNames'] = True
        
        request.session['uploaderInfo'] = uploaderInfo
        
        return redirect(finalPrompt)
    
    #############################################################################################################     
    elif request.method == 'GET':
        case1 = False
        if Helper.checkForSpecialCase(request.session):
            print('FOUND CASE 1')
            form.fields['hasSubjectID'].required = True
            form.fields['nameOfValueMeasured'].required = True 
            context['case1'] = True
            case1 = True
            
        if subjectRule == 'column':
            print('FOUND CASE 2 ')
            form.fields['hasSubjectID'].required = False
            context['case2'] = True
            
        if groupID == -1:
            print('FOUND CASE 3')
            form.fields['studyGroupDescription'].required = True 
            context['case3'] = True 
            
        if dcID == -1:
            print('FOUND CASE 4')
            form.fields['dataCategoryDescription'].required = True
            filenames = uploaderInfo.get('filenames')
            context['case4'] = True
        
        elif dcID == -1 and case1 is True: 
            print('FOUND CASE 5')
            form.fields['dataCategoryDescription'].required = True
            context['case5'] = True

                 
        print('\nGot Uploader Extra Info Request\n')
        
    #############################################################################################################
        
    context['form'] = form
    
    return render(request, 'uploader/extraInfo.html', context)



def finalPrompt(request):
    
    if Helper.pathIsBroken(request.session, True):
        return redirect(study)
    
    studyName = request.session['studyName']
    uploaderInfo = request.session['uploaderInfo']
    
    context = {
         'myCSS': 'uploaderFinalPrompt.css',
         'myJS': 'uploaderFinalPrompt.js',
         'studyName': studyName,
         'error': False
    }
    
    headers = uploaderInfo.get('headerInfo')
    isTimeSeries = uploaderInfo.get('isTimeSeries')
    subjectOrg = uploaderInfo.get('subjectOrganization')
    tableName = uploaderInfo.get('tableName')
    
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
        if Helper.checkForSpecialCase(request.session):
            colName, dataType = DBFunctions.getAttributeOfTable(tableName)
            uploaderInfo['specialInsert'] = { colName: {'position': '0', 'dataType': dataType} }
            request.session['uploaderInfo'] = uploaderInfo
            return redirect(upload)
            
        print('\nGot Uploader Extra Info Request\n')
        
    #############################################################################################################
    
    tableSchema = DBFunctions.getTableSchema(tableName)
    
    context['schema'] = tableSchema
    
    
    return render(request, 'uploader/finalPrompt.html', context)


def upload(request):
    
    if Helper.pathIsBroken(request.session):
        return redirect(study)
    
    studyName = request.session['studyName']
    positionInfo = request.session['positionInfo']
    uploaderInfo = request.session['uploaderInfo']
    filenames = uploaderInfo.get('filenames')
    hasSubjectNames = uploaderInfo.get('hasSubjectNames')
    print('Has Subject Names', hasSubjectNames)
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
            uploaderInfo['uploadedSuccessfully'] = True
            return HttpResponse(status=200)
        
        
    elif request.method == 'POST':
        
        specialFlag = False 
    
        key = 'specialInsert'
        if key in uploaderInfo.keys():
            positionInfo = uploaderInfo.get(key)
            specialFlag = True
        
        groupID = uploaderInfo.get('groupID')
        
        tableName = uploaderInfo.get('tableName')
        
        
        task = ProcessUpload.delay(filenames, uploaderInfo, positionInfo, specialFlag)
        
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


def error(request):
    context = {
         'myCSS': 'uploaderError.css'
    }
    
    
    if request.method == 'POST':
        Helper.clearUploadInfo(request.session)    
        Helper.deleteAllDocuments()
        return redirect(home)
    
    elif request.method == 'GET':
        if request.session.get('errorMessage', None) != None:
            context['errorMessage'] = request.session['errorMessage']
            
        if request.session.get('uploaderInfo', None) != None:
            uploaderInfo = request.session['uploaderInfo']
            filenames = uploaderInfo.get('filenames')

            uploaded, notUploaded = Helper.getUploadResults(filenames)
            
            context['uploaded'] = uploaded 
            context['notUploaded'] = notUploaded
            
        
    return render(request, 'uploader/errorPage.html', context) 


def success(request):
    context = {
         'myCSS': 'uploaderSuccess.css'
    }
    
    if request.method == 'POST':
        if 'finished' in request.POST:
            Helper.clearStudyName(request.session)
            return redirect(home)
        
        elif 'continue' in request.POST:
            Helper.clearUploadInfo(request.session) 
            return redirect(info)
        
    elif request.method == 'GET':
        if request.session.get('uploaderInfo', None) != None:
            uploaderInfo = request.session['uploaderInfo']
            filenames = uploaderInfo.get('filenames')

            uploaded, notUploaded = Helper.getUploadResults(filenames)
            
            context['uploaded'] = uploaded 
            context['notUploaded'] = notUploaded
        
    
    return render(request, 'uploader/successPage.html', context) 
    
    
            
        