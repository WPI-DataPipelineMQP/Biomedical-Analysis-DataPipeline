from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect
from django.core import serializers
from django.shortcuts import redirect
from .models import Document 
from . import views
from .database import DBClient, DBHandler 
from .viewHelpers import uploaderHelper as Helper
from .viewHelpers import uploaderDBFunctions as DBFunctions
from .uploaderForms import UploaderInfoForm, StudyNameForm, UploadInfoCreationForm, UploadPositionForm, StudyInfoForm

import pandas as pd
import numpy as np 

# FIRST PAGE
def uploaderStudy(request):
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
                            'label': studyNameForm[field].label,
                            'value': studyNameForm[field].data
                        }
                    )
            studyName = fields[0].get('value')
            request.session['studyName'] = studyName
            
            studyID = DBHandler.getSelectorFromTable('study_id', 'Study', [('study_name', studyName, True)], [None, None])
        
            if studyID == -1:
                # redirect to another page
                return redirect(uploaderStudyInfo)
            
            else:
                return redirect(uploaderInfo)
            
    #############################################################################################################           
    elif request.method == 'GET':
        print('\nGot Uploader Study Name Request\n')
        
        Helper.clearStudyName(request.session)
        Helper.clearUploadInfo(request.session)
        
        args = {
            'selectors': 'study_name',
            'from': 'Study',
            'join-type': None,
            'join-stmt': None,
            'where': None,
            'group-by': None,
            'order-by': None,
        }
    
        result = DBClient.executeQuery(args)
        cleanResult = []
        for item in result:
            study = item[0]
            cleanResult.append(study)
            
        
        context['studies'] = cleanResult
        
    #############################################################################################################
        
    
    form = StudyNameForm()
    
    context['form'] = form 
    
    return render(request, 'datapipeline/uploaderStudy.html', context)


# PAGE IF STUDY DOESN'T EXIST IN STUDY TABLE
def uploaderStudyInfo(request):
    
    if Helper.pathIsBroken(request.session, False):
        return redirect(uploaderStudy)
    
    
    studyName = request.session['studyName']
    
    context = {
         'myCSS': 'uploaderStudyInfo.css',
         'studyName': studyName,
         'error': False
    }
    
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
                values = [studyName, studyDescription, hasIRB, institutions, startDate, endDate, contactInfo, notes]
            
                DBHandler.insertToStudy(values)
            
                return redirect(uploaderInfo)
            
            else:
                context['error'] = True
            
        #############################################################################################################
        
    
    context['form'] = StudyInfoForm()
    
    return render(request, 'datapipeline/uploaderStudyInfo.html', context)


# PAGE THAT GETS THE UPLOADED CSV FILES
def uploaderInfo(request):
    
    if Helper.pathIsBroken(request.session):
        return redirect(uploaderStudy)
    
    studyName = request.session['studyName']
    
    context = {
         'myCSS': 'uploaderInfo.css',
         'studyName': studyName
    }
    
    #############################################################################################################
    if request.method == 'POST':
        uploaderForm = UploaderInfoForm(request.POST, request.FILES)
        fields = {}
        filenames = []
        
        if uploaderForm.is_valid():
            for field in uploaderForm.fields:
                if uploaderForm.cleaned_data[field]:
                    if field == 'uploadedFiles':
                        files = request.FILES.getlist(field)
                        
                        for file in files:
                            filenames.append(file.name)
                            newdoc = Document(uploadedFile = file, filename=file.name)
                            newdoc.save()
                        
                    else:
                        fields[field] = uploaderForm[field].data
        
        # READING THE CSV FILE
        firstFile = filenames[0]
        path = 'uploaded_csvs/{}'.format(firstFile)
        
        if Helper.hasHeaders(path) is False:
            request.session['errorMessage'] = "No Headers Were Included in the CSV File"
            return redirect(uploaderError)
            
        df = pd.read_csv(path) 
        
        headers = list(df.columns)
            
        fields['headerInfo'] = headers
            
        subjectOrgVal = fields.get('subjectOrganization')
        timeSeriesVal = fields.get('isTimeSeries')
        groupName = fields.get('groupName') 
        dataCategoryName = fields.get('categoryName')
        
        # MAKING THE NECESSARY DB QUERIES
        studyID = DBHandler.getSelectorFromTable('study_id', 'Study', [('study_name', studyName, True)], [None, None])
            
        where_params = [('study_group_name', groupName, True), ('study_id', studyID, False)]
        groupID = DBHandler.getSelectorFromTable('study_group_id', 'StudyGroup', where_params, [None, None])
            
        time_series_int = 0
            
        if timeSeriesVal == 'y':
            time_series_int = 1
                
        where_params = [('study_id', studyID, False), ('is_time_series', time_series_int, False), ('data_category_name', dataCategoryName, True)]

        join_stmt = 'DataCategoryStudyXref dcXref ON dc.data_category_id = dcXref.data_category_id'
        joinInfo = ['INNER JOIN', join_stmt]
    
        data_category_id = DBHandler.getSelectorFromTable('dc.data_category_id', 'DataCategory dc', where_params, joinInfo)
            
        if data_category_id != -1:
            fields = DBFunctions.handleDataCategoryID(data_category_id, fields)
            
        # UPDATING THE FIELDS
        fields['studyID'] = studyID
        fields['filenames'] = filenames
        fields['studyName'] = studyName
        fields['groupName'] = groupName
        fields['groupID'] = groupID
        fields['dcID'] = data_category_id
        fields['hasSubjectNames'] = False 
            
        # ALLOWING FIELDS TO BE PASSED AROUND
        request.session['uploaderInfo'] = fields 
        
        # CONDITIONS IF EXTRA INFORMATION IS NEEDED
        if (subjectOrgVal == 'row' and timeSeriesVal == 'y') or (groupID == -1) or (data_category_id == -1):

            return redirect(uploaderExtraInfo)
            
        else:
            return redirect(uploaderFinalPrompt)
    
    #############################################################################################################
          
    elif request.method == 'GET':
        print('\nGot Uploader Info Request\n')
        
        # get all the Study Groups and Data Categories for the Study and add to context
        
        studyID = DBHandler.getSelectorFromTable('study_id', 'Study', [('study_name', studyName, True)], [None, None])
        
        studyGroups = DBHandler.getInfoOnStudy('study_group_name', 'StudyGroup', [('study_id', studyID, False)], [None, None])
        
        where_params = [('study_id', studyID, False)]
        join_stmt = 'DataCategoryStudyXref dcXref ON dc.data_category_id = dcXref.data_category_id'
        joinInfo = ['INNER JOIN', join_stmt]
    
        dataCategories = DBHandler.getInfoOnStudy('dc.data_category_name', 'DataCategory dc', where_params, joinInfo)
        
        context['studyGroups'] = studyGroups
        context['dataCategories'] = dataCategories
    
    #############################################################################################################
    
    
    form = UploaderInfoForm()
    
    context['form'] = form
    
    return render(request, 'datapipeline/uploaderInfo.html', context)


def uploaderExtraInfo(request):
    
    if Helper.pathIsBroken(request.session, True):
        return redirect(uploaderStudy)
    
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
    
    form = UploadInfoCreationForm(None, dynamicFields=headers)
    
    ############################################################################################################# 
    if request.method == 'POST':
        form = UploadInfoCreationForm(request.POST, dynamicFields=headers)
        form.reset()
        
        print(form.errors)
        myFields = {}
        myExtras = []
        if form.is_valid():
            for (i, val) in form.getAllFields():
                myFields[i] = val 
            
            for (name, val) in form.getExtraFields():
                myExtras.append((name, val))
        
        print(myFields)
        if subjectRule == 'row' and isTimeSeries == 'y':
            colName = myFields.get('nameOfValueMeasured')
            dataType = myFields.get('datatypeOfMeasured')
            dataType = Helper.getActualDataType(dataType)
            uploaderInfo['specialInsert'] = { colName: {'position': '0', 'dataType': dataType} }
            
        if groupID == -1:
            description = myFields.get('studyGroupDescription')
            DBHandler.insertToStudyGroup(groupName, description, studyID) 
            
            where_params = [('study_group_name', groupName, True), ('study_id', studyID, False)]
            groupID = DBHandler.getSelectorFromTable('study_group_id', 'StudyGroup', where_params, [None, None])
            
            uploaderInfo['groupID'] = groupID
            
            
        if dcID == -1:
            uploaderInfo, errorMessage = DBFunctions.handleMissingDataCategoryID(studyID, subjectRule, isTimeSeries, uploaderInfo, [myFields, myExtras])
            
            if errorMessage is not None:
                request.session['errorMessage'] = errorMessage + " Please review the guidelines carefully and make sure your files follow them."
                return redirect(uploaderError)
            
        
        request.session['uploaderInfo'] = uploaderInfo
        
        return redirect(uploaderFinalPrompt)
    
    #############################################################################################################     
    elif request.method == 'GET':
        case1 = False
        if subjectRule == 'row' and isTimeSeries == 'y':
            print('FOUND CASE 1')
            form.fields['hasSubjectID'].required = True
            form.fields['nameOfValueMeasured'].required = True 
            context['case1'] = True
            case1 = True
            form = UploadInfoCreationForm(None, dynamicFields=[])
            
        elif subjectRule == 'row':
            print('FOUND CASE 2 ')
            form.fields['hasSubjectID'].required = True
            context['case2'] = True
            
        if groupID == -1:
            print('FOUND CASE 3')
            form.fields['studyGroupDescription'].required = True 
            context['case3'] = True 
            
        if dcID == -1 and case1 is False:
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
    
    return render(request, 'datapipeline/uploaderExtraInfo.html', context)



def uploaderFinalPrompt(request):
    
    if Helper.pathIsBroken(request.session, True):
        return redirect(uploaderStudy)
    
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
    
    #############################################################################################################
    if request.method == 'POST':
        form = UploadPositionForm(request.POST, columns=headers)
        myFields = []
        
        if form.is_valid():
            for (i, val) in form.getColumnFields():
                myFields.append((i, val)) 
        
        clean = Helper.seperateByName(myFields, 2, True)       
        
        if Helper.foundDuplicatePositions(clean) is True:
            print('Found Duplicate!')
            context['error'] = True
            
        else:
            request.session['positionInfo'] = clean 
            
            return redirect(uploader)
            
    #############################################################################################################
    elif request.method == 'GET':
        if isTimeSeries and subjectOrg == 'row':
            print(uploaderInfo)
            return redirect(uploader)
            
        print('\nGot Uploader Extra Info Request\n')
        
    #############################################################################################################
    
    tableSchema = DBFunctions.getTableSchema(tableName)
    
    context['schema'] = tableSchema
    context['form'] = form
    
    return render(request, 'datapipeline/uploaderFinalPrompt.html', context)


def uploader(request):
    
    if Helper.pathIsBroken(request.session):
        return redirect(uploaderStudy)
    
    studyName = request.session['studyName']
    
    context = {
         'myCSS': 'uploader.css',
         'studyName': studyName
    }
    
    if request.method == 'POST':
        positionInfo = request.session['positionInfo']
        uploaderInfo = request.session['uploaderInfo']
        specialFlag = False 
    
        key = 'specialInsert'
        if key in uploaderInfo.keys():
            positionInfo = uploaderInfo.get(key)
            specialFlag = True
        
           
        filenames = uploaderInfo.get('filenames')
        groupID = uploaderInfo.get('groupID')
        hasSubjectNames = uploaderInfo.get('hasSubjectNames')
        tableName = uploaderInfo.get('tableName')
    
        columnInfo = []
        organizedColumns = []
    
        # put this in a POST
        path = 'uploaded_csvs/'
        noError = True 
        errorMessage = None
        for i, file in enumerate(filenames):
            filepath = path + file
            if i == 0:
                columnInfo, organizedColumns = Helper.getInfo(positionInfo)
        
            if specialFlag is True:
                noError, errorMessage = DBFunctions.specialUploadToDatabase(filepath, uploaderInfo, columnInfo)
            
            else:
                noError, errorMessage = DBFunctions.uploadToDatabase(filepath, file, uploaderInfo, columnInfo, organizedColumns)
                
            if noError is False:
                request.session['errorMessage'] = errorMessage + " Please review the guidelines carefully and make sure you did not make any mistakes during the uploader process."
                return redirect(uploaderError)
            
            
        print('Upload Completed!')
            
    
        # DELETING UPLOADED CSV FILES
        for name in filenames:
            tmpPath = path + name
            instance = Document.objects.get(uploadedFile=tmpPath, filename=name)
            instance.uploadedFile.delete()
            instance.delete()
            
        return redirect(uploaderSuccess)
    
        
    return render(request, 'datapipeline/uploader.html', context) 


def uploaderError(request):
    context = {
         'myCSS': 'uploaderError.css'
    }
    
    
    if request.method == 'POST':
        Helper.clearUploadInfo(request.session)    
        return redirect(views.home)
    
    elif request.method == 'GET':
        if request.session.get('errorMessage', None) != None:
            context['errorMessage'] = request.session['errorMessage']
            
        Helper.deleteAllDocuments()
        
    
    return render(request, 'datapipeline/uploaderError.html', context) 


def uploaderSuccess(request):
    context = {
         'myCSS': 'uploaderSuccess.css'
    }
    
    if request.method == 'POST':
        if 'finished' in request.POST:
            Helper.clearStudyName(request.session)
            return redirect(views.home)
        
        elif 'continue' in request.POST:
            Helper.clearUploadInfo(request.session) 
            return redirect(uploaderInfo)
    
    return render(request, 'datapipeline/uploaderSuccess.html', context) 
    
    
            
        