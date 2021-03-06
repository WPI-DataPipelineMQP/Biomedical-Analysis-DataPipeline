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
from django.db.models import Q
from django.conf import settings

from datapipeline.views import home
from datapipeline.database import DBClient
from datapipeline.models import Study, StudyGroup, DataCategory, DataCategoryStudyXref

from .viewHelpers import Helper, DBFunctions
from . import views
from .forms import UploaderInfoForm, StudyNameForm, UploadInfoCreationForm, UploadPositionForm, StudyInfoForm, DisabledInputForm
from .tasks import ProcessUpload
from .uploaderinfo import UploaderInfo

import celery, jsonpickle, re, json


'''
Handles back end for gathering the study to upload to
'''
@login_required
def study(request):
    context = {
         'myCSS': 'uploaderStudy.css',
    }
    
    allStudies = Study.objects.filter(
            (Q(visibility="Public (Testing)") | Q(owner=request.user.id))
        )
        
    studyNames = [ (study.study_name,study.study_name) for study in allStudies ]
    
    form = StudyNameForm(studies=studyNames)
    
    
    #############################################################################################################
    if request.method == 'POST':
        studyNameForm = StudyNameForm(request.POST, studies=studyNames)
        fields = {}
        
        if studyNameForm.is_valid():
            for field in studyNameForm.fields:
                if studyNameForm.cleaned_data[field]:
                    fields[field] = studyNameForm[field].data 
        

        studyName = fields.get('otherStudy', '')
        
        if 'which_study_field' in fields.keys():
            user_input = fields['which_study_field'] 
            if user_input == 'y':
                studyName = fields['existingStudies']
                
            else:
                if len(studyName) == 0:
                    msg = 'Detected an Empty Study Name. If you are adding a new study, please enter one in' 
                    messages.error(request, msg)
                    
                    context['form'] = studyNameForm 
                    
                    return render(request, 'uploader/studyName.html', context)  
                
        request.session['studyName'] = studyName
        
        studyExists = Study.objects.filter(
            (Q(visibility="Public (Testing)") | Q(owner=request.user.id)),
            study_name=studyName
        ).exists()
        
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

        
    #############################################################################################################
        
    context['form'] = form 
    
    return render(request, 'uploader/studyName.html', context)


'''
If study does not exist in database, this method will be called which is in charge of collecting the meta data
for the new study and adding it to the database
'''
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
                if Study.objects.filter(study_name=studyName, owner=request.user).exists() is False:
                    # doing a insert to the Study table through using Django Models
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


'''
This is the method that is in charge of handling the backend of the info page. At this page it will need to check to make sure the 
uploaded documents are acceptable and detect if the user is uploading duplicate files.
'''
@login_required
def info(request):
    
    if Helper.pathIsBroken(request.session):
        return redirect(study)
    
    studyName = request.session['studyName']
    
    context = {
         'myCSS': 'uploaderInfo.css',
         'studyName': studyName
    }
    
    studyID = (Study.objects.get(
        (Q(visibility="Public (Testing)") | Q(owner=request.user.id)),
        study_name=studyName
    )).study_id
    
    form = UploaderInfoForm(id=studyID)
    #############################################################################################################
    if request.method == 'POST':
        checkedForDuplications = request.session['checkedForDuplications']        
        defaultGroup = False
        uploaderForm = UploaderInfoForm(request.POST, request.FILES, id=studyID)
        
        if uploaderForm.is_valid():
            files = request.FILES.getlist('uploadedFiles')
            
            fields, filenames = Helper.getFieldsFromInfoForm(uploaderForm, files)
            
        '''
        The following 3 if statements are to check if user chose an existing data category and/or study group or 
        decided to add a new one
        
        NOTE: certain fields found will help in the detection. Refer to the uploader/forms.py for reference
        '''
        if 'which-category-field' in fields.keys():
            user_input = fields['which-category-field'] 
            if user_input == 'y':
                fields['categoryName'] = fields['existingCategory']
        
        if 'groupName' not in fields.keys():
            defaultGroup = True
            fields['groupName'] = '(default)'
            
        if 'which-group-field' in fields.keys():
            user_input = fields['which-group-field'] 
            if user_input == 'y':
                fields['groupName'] = fields['existingStudyGroup']
        
        uploaderInfo = UploaderInfo(studyName)
        uploaderInfo.studyID = studyID
        uploaderInfo.groupName = fields.get('groupName')
        uploaderInfo.subjectOrganization = fields.get('subjectOrganization')
        rawTimeSeries = fields.get('isTimeSeries')
        uploaderInfo.isTimeSeries = True if rawTimeSeries == 'y' else False
        
        # this block checks for any uploaded files that are not named correctly
        if (uploaderInfo.subjectOrganization == 'file'):
            if not Helper.passFilenameCheck(filenames):
                msg = "Detected an error in the filename of the uploaded files. \
                    If the format is by Subject per File, please follow the convention when naming the files. \
                    Please reupload the file with the correct file name"
                messages.error(request, msg) 
                
                if not checkedForDuplications:
                    uploaderForm.fields['handleDuplicate'].widget = forms.HiddenInput()
                    
                Helper.deleteAllDocuments()
                
                context['form'] = uploaderForm 
                
                return render(request, 'uploader/info.html', context)
        
        
        uploaderInfo.categoryName = Helper.cleanCategoryName(fields.get('categoryName'))
        
        uploaderInfo.handleDuplicate = fields.get('handleDuplicate', 'N/A')
        
        data_category_id = DBFunctions.getDataCategoryIDIfExists(uploaderInfo.categoryName, uploaderInfo.isTimeSeries, uploaderInfo.subjectOrganization, studyID)
        
        # checking if data category already exists
        if data_category_id != -1:
            uploaderInfo.updateFieldsFromDataCategory(data_category_id)
            
        elif data_category_id == -1 and fields.get('which-category-field') == 'y':
            msg = 'Detected an attempted to create a table using a name that already exists in the database! Please enter in a name that is not displayed in the dropdown'
            messages.error(request, msg)
            
            if not checkedForDuplications:
                uploaderForm.fields['handleDuplicate'].widget = forms.HiddenInput()
            context['form'] = uploaderForm 
                
            return render(request, 'uploader/info.html', context)
        
        # reset the checkedForDuplications flag to put user back into loop for detecting duplicate files
        if uploaderInfo.handleDuplicate == 'N/A':
            checkedForDuplications = False 
        
        # this block handles duplicate files
        if checkedForDuplications is False or uploaderInfo.handleDuplicate == 'newFile':
            duplicateFiles = []
            for filename in filenames:
                if uploaderInfo.documentExists(filename):
                    duplicateFiles.append(filename)
                    
            if len(duplicateFiles) > 0:
                uploaderForm.fields['handleDuplicate'].required = True
                context['form'] = uploaderForm 
                print('Found Duplicate File!')
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
        
        # checking for a special case that will be needed to be treated differently
        if uploaderInfo.isTimeSeries and (uploaderInfo.subjectOrganization == 'row' or uploaderInfo.subjectOrganization == 'column'):
            if uploaderInfo.subjectOrganization == 'row':
                specialRow = True 
                
            specialFlag = True
        
        uploaderInfo.specialCase = specialFlag 

        firstFile = filenames[0]
        
        df = Helper.getDataFrame(firstFile)
        
        if specialRow is False and Helper.hasAcceptableHeaders(df) is False:
            request.session['errorMessage'] = "No Headers Were Detected in the CSV File"
            uploaderInfo.uploadedFiles = filenames
            request.session['uploaderInfo'] = jsonpickle.encode(uploaderInfo)
            return redirect(error)
        
        headers, hasSubjectNames, subjectPerCol = Helper.extractHeaders(df, uploaderInfo.subjectOrganization)
        
        uploaderInfo.headers = headers
        
        groupID = DBFunctions.getGroupID(uploaderInfo.groupName, studyID)

        # Set default description and insert study group here if using the default study group for the first time
        if groupID == -1 and defaultGroup:
            description = "This is the default study group if no study group is specified."
            DBFunctions.insertToStudyGroup(uploaderInfo.groupName, description, studyID)
            
        groupID = DBFunctions.getGroupID(uploaderInfo.groupName, studyID)
        
        uploaderInfo.groupID = groupID
        uploaderInfo.dcID = data_category_id
        uploaderInfo.subjectPerCol = subjectPerCol
        uploaderInfo.hasSubjectNames = hasSubjectNames
        uploaderInfo.uploadedFiles = filenames
        
        
        # ALLOWING FIELDS TO BE PASSED AROUND
        request.session['uploaderInfo'] = jsonpickle.encode(uploaderInfo)
        
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
    
    #############################################################################################################
    
    form.fields['handleDuplicate'].widget = forms.HiddenInput()
    context['form'] = form
    
    return render(request, 'uploader/info.html', context)

'''
This method handles the backend when the user is entering something new to the database that the system needs 
to collect meta data on
'''
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
        
        myFields, myExtras = {}, []     # making it easier to read the raw collected data 
        
        if form.is_valid():
            for (i, val) in form.getAllFields():
                myFields[i] = val 
            
            for (name, val) in form.getExtraFields():
                myExtras.append((name, val))
        
        # handles a special case scenario (is heartrate == True and Subject per Row)
        if uploaderInfo.specialCase:
            colName = myFields.get('nameOfValueMeasured').lower()
            dataType = myExtras[0][1]
            dataType = Helper.getActualDataType(dataType)
            uploaderInfo.specialInsert = { colName: {'position': '0', 'dataType': dataType} }
            myExtras = Helper.replaceWithNameOfValue(myExtras, colName)
            
        if subjectRule == 'column':
            myFields['hasSubjectID'] = 'y'      # automatic yes
            
        # makes any necessary inserts to the StudyGroup table
        if groupID == -1:
            description = myFields.get('studyGroupDescription')
            
            DBFunctions.insertToStudyGroup(groupName, description, studyID)
            
            groupID = DBFunctions.getGroupID(groupName, studyID)
            
            uploaderInfo.groupID = groupID
            
        # makes any necessary inserts to the DataCategory table
        if dcID == -1:
            errorMessage = uploaderInfo.handleMissingDataCategoryID(myFields, myExtras)
            
            if errorMessage is not None:
                request.session['errorMessage'] = errorMessage + " Please review the guidelines carefully and make sure your files follow them."
                return redirect(error)
        
        if uploaderInfo.subjectPerCol is True:
            uploaderInfo.hasSubjectNames = True
        
        request.session['uploaderInfo'] = jsonpickle.encode(uploaderInfo)
        
        return redirect(finalPrompt)
    
    #############################################################################################################     
    elif request.method == 'GET':
        # if statements will determine which meta data will be shown to the user to be filled out        
        if uploaderInfo.specialCase:
            form.fields['nameOfValueMeasured'].required = True
            
            context['case1'] = True
            if subjectRule == 'column':
                form.fields['hasSubjectID'].required = False
                context['withSubjectID'] = False
            
            else:
                context['withSubjectID'] = True


        if groupID == -1:
            form.fields['studyGroupDescription'].required = True 
            context['case2'] = True 

        if dcID == -1:
            form.fields['dataCategoryDescription'].required = True
            context['case3'] = True

        
    #############################################################################################################
        
    context['form'] = form
    
    return render(request, 'uploader/extraInfo.html', context)


'''
This handles the backend for the page that asks for the user to position the columns from the uploaded files
to their corresponding columns within the database table
'''
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
        
        
        clean = Helper.seperateByName(myFields, 1, True, True, dcID)   # cleans the raw data to be easier to parse through

        if clean is None:
            request.session['errorMessage'] = "Invalid number of columns found in uploaded CSV file"
            return redirect(error)
        
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

'''
This method handles the backend for the actual uploading process. It will use all the collected information
to make the upload to the database. It will do the uploading asynchronously by putting the functionality 
into a task
'''
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
        
        # checks if uploading needs to handle it differently
        if uploaderInfo.specialInsert != '':
            positionInfo = uploaderInfo.specialInsert
            specialFlag = True
            
        # calling the async function to upload the data
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

'''
This handles the backend for the error page. Essentially it will display the error message and also 
provide information to the user of which of the uploaded files were uploaded successfully or not
'''
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

'''
This handles the backend of the success page. It simply just informs the user that the uploaded files were
uploaded successfully.
'''
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
