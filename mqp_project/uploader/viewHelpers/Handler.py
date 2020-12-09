from django.db import IntegrityError, transaction
from datapipeline.database import DBClient
from datapipeline.models import Study, StudyGroup, Subject, DataCategory, DataCategoryStudyXref
from ..models import Document

from . import Helper, DBFunctions

import pandas as pd 
import numpy as np

def documentExists(filename, category_name, timeSeries, studyID):
    dcID = DBFunctions.getDataCategoryIDIfExists(category_name, timeSeries, studyID)
    
    if dcID != -1:
        dcObj = DataCategory.objects.get(data_category_id=dcID) 
        exists = Document.objects.filter(filename=filename, data_category=dcObj).exists()
        
        return exists 
    
    return False 


def updateFieldsFromDataCategory(data_category_id, fields):

    tableName = (DataCategory.objects.get(data_category_id=data_category_id)).dc_table_name
    isTimeSeries = (DataCategory.objects.get(data_category_id=data_category_id)).is_time_series
    hasSubjectNames = (DataCategory.objects.get(data_category_id=data_category_id)).has_subject_name
                
    fields['tableName'] = tableName
    fields['isTimeSeries'] = isTimeSeries
    fields['hasSubjectNames'] = hasSubjectNames
    
    return fields


def dataCategoryHandler(myMap, study_id):
    
    data_category_name = myMap.get('categoryName')
    
    time_series = myMap.get('isTimeSeries')
    has_subjectNames = myMap.get('hasSubjectNames')
        
    myMap['createTable'] = False
    
    description = myMap.get('DC_description')
    dc_table_name = data_category_name + '_' + str(study_id)
    
    insertSuccess = DBFunctions.insertToDataCategory(data_category_name, time_series, has_subjectNames, dc_table_name, description)
    
    if insertSuccess is False:
        return myMap, False
    
    data_category_id = DBFunctions.getDataCategoryID(dc_table_name, time_series)
    
    myMap['DC_ID'] = data_category_id
        
    insertSuccess = DBFunctions.insertToDataCategoryXref(data_category_id, study_id)

    if insertSuccess is False:
        return myMap, False
    
    
    data_category_name = data_category_name.replace(" ", "_")
    myMap['tableName'] = data_category_name + '_' + str(study_id)

    return myMap, True



def handleMissingDataCategoryID(studyID, subjectRule, isTimeSeries, uploaderInfo, otherInfo):
    errorMessage = ''
    hasSubjectNames = False 
    
    myFields, myExtras = otherInfo[0], otherInfo[1]
            
    subjectVal = myFields.get('hasSubjectID')
            
    if subjectVal == 'y':
        hasSubjectNames = True 
            
         
    uploaderInfo['hasSubjectNames'] = hasSubjectNames 
    uploaderInfo['isTimeSeries'] = isTimeSeries
                       
    myMap = {
        'categoryName': uploaderInfo.get('categoryName'),
        'isTimeSeries': isTimeSeries,
        'hasSubjectNames': hasSubjectNames,
        'DC_description': myFields.get('dataCategoryDescription')
    }
    
    cleanResult = Helper.organizeExtraColsDataType(myExtras)
    
    try:
        with transaction.atomic():
            myMap, noErrors = dataCategoryHandler(myMap, studyID) 
                
            if noErrors is False:
                errorMessage = "Error found when updating the DataCategory Table!"
                raise IntegrityError()
            
            uploaderInfo['tableName'] = myMap.get('tableName')
            uploaderInfo['dcID'] = myMap.get('DC_ID')
            
            myMap['columns'] = cleanResult

            cleanAttributeFormat = Helper.seperateByName(myExtras, 4, False)
            
            noErrors = DBFunctions.insertToAttribute(cleanAttributeFormat, myMap.get('DC_ID'))

            if noErrors is False:
                errorMessage = "Error found when inserting to Attribute table!"
                raise IntegrityError()
            
            noErrors = DBFunctions.createNewTable(myMap)
            
            if noErrors is False:
                errorMessage = "Error found when creating the new table!"
                raise IntegrityError()
                
    except IntegrityError:
        print('SHOULD ROLLBACK')

        return uploaderInfo, errorMessage
    
    
    return uploaderInfo, None



def subjectHandler(filename, study_group_id, subjectNumber=None):
    subject_number = subjectNumber
    
    if subjectNumber is None:
        subject_number = filename.split('_')[0] 
        
    
    subject_id = DBFunctions.getSubjectID(subject_number, study_group_id)
    
    if subject_id == -1:
        insertSuccess = DBFunctions.insertToSubject(subject_number, study_group_id)
        
        if insertSuccess is False:
            errorMessage = 'ERROR: Error Found When Attempting to Insert Subject_Number: {} and Study Group ID: {} to Subject Table'.format(subject_number, study_group_id)
            
            return -1, errorMessage
        
        subject_id = DBFunctions.getSubjectID(subject_number, study_group_id)
        
    
    return subject_id, None


def specialUploadToDatabase(file, docID, myMap, column_info):
    groupID = myMap.get('groupID')
    tableName = myMap.get('tableName')
    
    columnHeaders = DBClient.getTableColumns(tableName)
    
    columnName = column_info[0][0]
    dt = column_info[0][1]
    
    df = pd.read_csv(file)
    
    if myMap.get('subjectPerCol') is True:
        df = Helper.transposeDataFrame(df, True)
    
    numpyArray = df.to_numpy()

    try:
        myDf = pd.DataFrame(columns=[columnName, 'subject_id', 'doc_id']) 
        with transaction.atomic():
            for i, row in enumerate(numpyArray):
                                
                subject_number = i 
        
                if myMap.get('hasSubjectNames') is True:
                    subject_number = row[0]
                    row = row[1:]
        
                subject_id, noError = subjectHandler("", groupID, subject_number)

                if noError is False:
                    raise Exception()
        
                tmpDf = pd.DataFrame(row, columns=[columnName])

                if dt == 1:
                    tmpDf[[columnName]].astype(str)

                elif dt == 2:
                    tmpDf[[columnName]].astype(int)

                elif dt == 3:
                    tmpDf[[columnName]].astype(float)

                elif dt == 4:
                    tmpDf[columnName] = pd.to_datetime(df[columnName])
                    tmpDf[columnName] = df[columnName].dt.strftime('%Y-%m-%d %H:%M:%S')
            
                else:
                    tmpDf[columnName].astype(bool)
            
                tmpDf['subject_id'] = subject_id
                tmpDf['doc_id'] = docID
                
                myDf = myDf.append(tmpDf, ignore_index=True)


            

        DBClient.dfInsert(myDf, tableName)
        print('ALL DONE')
            
    except Exception as e:
        errorMessage = str(e)
        return False, errorMessage     
    
    return True, None



def uploadToDatabase(file, filename, docID, myMap, column_info, organizedColumns):
    errorMessage = None
    columnFlag = False 
    df = pd.read_csv(file)
    
    if myMap.get('subjectPerCol') is True:
        columnFlag = True
        df = Helper.transposeDataFrame(df, True)
        
    
    filename = Helper.modifyFileName(filename)
    groupID = myMap.get('groupID')
    
    tableName = myMap.get('tableName')
        
    # fix error handler
    if myMap.get('hasSubjectNames') is True:
        listOfSubjects, listOfSubjectNum = [], []
        
        if columnFlag is True:
            listOfSubjectNum = list(df.index)
        else:
            listOfSubjectNum = list(df.iloc[:,0])
        
        for num in listOfSubjectNum:
            if isinstance(num, str):
                num = num.upper()
                
            currID, errorMessage = subjectHandler("", groupID, num)
            listOfSubjects.append(currID)
        
        
        df = df.drop(df.columns[0], axis=1) # deleting the subjects column
        
        df = df[organizedColumns]
        df['subject_id'] = listOfSubjects
        
        
    else:
        subjectID, errorMessage = subjectHandler(filename, groupID)
        
        df = df[organizedColumns]
        df['subject_id'] = subjectID
    
    df['doc_id'] = docID
        
    try:
        with transaction.atomic():
            for col in column_info:
                col_name = col[0]
                dt = col[1]
        
                if dt == 1:
                    df[[col_name]].astype(str)

                elif dt == 2:
                    df[[col_name]].astype(int)

                elif dt == 3:
                    df[[col_name]].astype(float)

                elif dt == 4:
                    df[col_name] = pd.to_datetime(df[col_name])
                    df[col_name] = df[col_name].dt.strftime('%Y-%m-%d %H:%M:%S')
            
                else:
                    df[col_name].astype(bool)
    
            columnHeaders = DBClient.getTableColumns(tableName)
    
            if len(columnHeaders) == 0:
                errorMessage = "ERROR: found no column headers for {} table".format(tableName)
                raise Exception()
            
            
            columnHeaders = columnHeaders[1:]
        
            df.columns = columnHeaders

            DBClient.dfInsert(df, tableName)
    
    except Exception as e:
        if errorMessage is None:
            #errorMessage = "Error found when trying to insert to the {} table. Most likely an incorrect data type was specified for one of the columns.".format(tableName)
            errorMessage = str(e)
        return False, errorMessage     
    
    return True, None
        