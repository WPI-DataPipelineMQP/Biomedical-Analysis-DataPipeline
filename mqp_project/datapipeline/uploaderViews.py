from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import HttpResponseRedirect
from django.core import serializers
from django.shortcuts import redirect
from .models import Document 
from .database import DBClient, DBHandler 
from . import uploaderViewHelper as Helper
from .uploaderForms import UploaderInfoForm, StudyNameForm, UploadInfoCreationForm

import pandas as pd
import numpy as np 

    
def uploaderExtraInfo(request):
    studyName = request.session['studyName']
    uploaderInfo = request.session['uploaderInfo']
    
    context = {
         'myCSS': 'uploaderInfo.css',
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
        print(uploaderInfo)
        if groupID == -1:
            description = myFields.get('studyGroupDescription')
            DBHandler.insertToStudyGroup(groupName, description, studyID) 
        
        if dcID == -1:
            isTS = False 
            
            if isTimeSeries == 'y':
                isTS = True 
                
            myMap = {
                'categoryName': uploaderInfo.get('categoryName'),
                'isTimeSeries': isTS,
                'DC_description': myFields.get('dataCategoryDescription')
            }
            
            myMap = DBHandler.dataCategoryHandler(myMap, studyID)
            
            cleanResult = Helper.getCleanFormat(myExtras)
            
            myMap['columns'] = cleanResult
            
            DBHandler.newTableHandler(myMap)
            # create table
        
      
    elif request.method == 'GET':
        if subjectRule == 'row' and isTimeSeries == 'y':
            print('FOUND CASE 1')
            form.fields['hasSubjectID'].required = True
            form.fields['nameOfValueMeasured'].required = True 
            context['case1'] = True
            
        if groupID == -1:
            print('FOUND CASE 2')
            form.fields['studyGroupDescription'].required = True 
            context['case2'] = True 
            
        if dcID == -1:
            print('FOUND CASE 3')
            form.fields['dataCategoryDescription'].required = True
            filenames = uploaderInfo.get('filenames')
            form = UploadInfoCreationForm(None, dynamicFields=headers)
            context['case3'] = True
                
        print('\nGot Uploader Extra Info Request\n')
        
    
    context['form'] = form
    
    return render(request, 'datapipeline/uploaderExtraInfo.html', context) 
    
    
    
def uploaderInfoGathering(request):
    studyName = request.session['studyName']
    
    context = {
         'myCSS': 'uploaderInfo.css',
         'studyName': studyName
    }
    
    if request.method == 'POST':
        uploaderForm = UploaderInfoForm(request.POST, request.FILES)
        fields = {}
        filenames = []
        
        if uploaderForm.is_valid():
            for field in uploaderForm.fields:
                if uploaderForm.cleaned_data[field]:
                    if field == 'uploadedFiles':
                        files = request.FILES.getlist(field)
                        count = len(files)
                        for file in files:
                            filenames.append(file.name)
                            newdoc = Document(uploadedFile = file, filename=file.name)
                            newdoc.save()
                        
                    else:
                        fields[field] = uploaderForm[field].data
            
            firstFile = filenames[0]
            path = 'uploaded_csvs/{}'.format(firstFile)
            df = pd.read_csv(path) 
            headers = list(df.columns)
            
            fields['headerInfo'] = headers
            
            # for deleting
            path = 'uploaded_csvs/'
            for name in filenames:
                tmpPath = path + name
                instance = Document.objects.get(uploadedFile=tmpPath, filename=name)
                instance.uploadedFile.delete()
                instance.delete()
            
            subjectOrgVal = fields.get('subjectOrganization')
            timeSeriesVal = fields.get('isTimeSeries')
            groupName = fields.get('groupName') 
            dataCategoryName = fields.get('categoryName')
            
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
            
            fields['studyID'] = studyID
            fields['filenames'] = filenames
            fields['studyName'] = studyName
            fields['groupName'] = groupName
            fields['groupID'] = groupID
            fields['dcID'] = data_category_id
            
            # do any table creations or db lookups here
            request.session['uploaderInfo'] = fields 
            
            if (subjectOrgVal == 'row' and timeSeriesVal == 'y') or (groupID == -1) or (data_category_id == -1):
                print('\nFound Special Handler\n')
                return redirect(uploaderExtraInfo)
        else:
            print('Not Valid')
            
    elif request.method == 'GET':
        print('\nGot Uploader Info Request\n')
        
        studyID = DBHandler.getSelectorFromTable('study_id', 'Study', [('study_name', studyName, True)], [None, None])
        
        if studyID == -1:
            # redirect to another page
            return None
        
        studyGroups = DBHandler.getInfoOnStudy('study_group_name', 'StudyGroup', [('study_id', studyID, False)], [None, None])
        
        where_params = [('study_id', studyID, False)]
        join_stmt = 'DataCategoryStudyXref dcXref ON dc.data_category_id = dcXref.data_category_id'
        joinInfo = ['INNER JOIN', join_stmt]
    
        dataCategories = DBHandler.getInfoOnStudy('dc.data_category_name', 'DataCategory dc', where_params, joinInfo)
        
        context['studyGroups'] = studyGroups
        context['dataCategories'] = dataCategories
    
    
    # get all the Study Groups and Data Categories for the Study and add to context
    
    form = UploaderInfoForm()
    
    context['form'] = form
    
    return render(request, 'datapipeline/uploaderInfo.html', context) 


def uploaderStudyName(request):
    
    context = {
         'myCSS': 'uploaderStudyName.css',
    }
    
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
            print(studyName)
            
            return redirect(uploaderInfoGathering)
            
            
            
    elif request.method == 'GET':
        print('\nGot Uploader Study Name Request\n')
        
        args = {
            'selectors': '*',
            'from': 'Study',
            'join-type': None,
            'join-stmt': None,
            'where': None,
            'group-by': None,
            'order-by': None,
        }
    
        result = DBClient.executeQuery(args)
        
        context['studies'] = result
        
    
    form = StudyNameForm()
    
    context['form'] = form 
    
    return render(request, 'datapipeline/uploaderStudyName.html', context)