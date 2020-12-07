from django.db import IntegrityError, transaction
from datapipeline.database import DBClient, DBHandler
from . import Helper 
import pandas as pd 
import numpy as np


def handleDataCategoryID(data_category_id, fields):
    where_params = [('data_category_id', data_category_id, False)]
                
    tableName = DBHandler.getSelectorFromTable('dc_table_name', 'DataCategory', where_params, [None, None])
    isTimeSeries = DBHandler.getSelectorFromTable('is_time_series', 'DataCategory', where_params, [None, None])
    hasSubjectNames = DBHandler.getSelectorFromTable('has_subject_name', 'DataCategory', where_params, [None, None])
                
    fields['tableName'] = tableName
    fields['isTimeSeries'] = isTimeSeries
    fields['hasSubjectNames'] = hasSubjectNames
    
    return fields

def handleMissingDataCategoryID(studyID, subjectRule, isTimeSeries, uploaderInfo, otherInfo):
    errorMessage = ''
    isTS = False 
    hasSubjectNames = False 
    
    myFields, myExtras = otherInfo[0], otherInfo[1]
            
    subjectVal = myFields.get('hasSubjectID')
            
    if subjectVal == 'y':
        hasSubjectNames = True 
            
    if isTimeSeries == 'y':
        isTS = True 
                
    uploaderInfo['hasSubjectNames'] = hasSubjectNames 
    uploaderInfo['isTimeSeries'] = isTS
                       
    myMap = {
        'categoryName': uploaderInfo.get('categoryName'),
        'isTimeSeries': isTS,
        'hasSubjectNames': hasSubjectNames,
        'DC_description': myFields.get('dataCategoryDescription')
    }
    
    cleanResult = Helper.getCleanFormat(myExtras)
    
    try:
        with transaction.atomic():
            myMap, noErrors = DBHandler.dataCategoryHandler(myMap, studyID) 
                
            if noErrors is False:
                errorMessage = "Error found when updating the DataCategory Table!"
                raise IntegrityError()
            
            uploaderInfo['tableName'] = myMap.get('tableName')
            uploaderInfo['dcID'] = myMap.get('DC_ID')
            
            myMap['columns'] = cleanResult
            
            print(myExtras)
            cleanAttributeFormat = Helper.seperateByName(myExtras, 4, False)
            
            print(cleanAttributeFormat)
            
            noErrors = DBHandler.insertToAttribute(cleanAttributeFormat, myMap.get('DC_ID'))

            if noErrors is False:
                errorMessage = "Error found when inserting to Attribute table!"
                raise IntegrityError()
            
            noErrors = DBHandler.newTableHandler(myMap)
            
            print(noErrors)
            if noErrors is False:
                errorMessage = "Error found when creating the new table!"
                raise IntegrityError()
                
    except IntegrityError:
        print('SHOULD ROLLBACK')

        return uploaderInfo, errorMessage
    
    
    return uploaderInfo, None


def getTableSchema(tableName):
    string = '{} SCHEMA: '.format(tableName)
    
    columns = DBClient.getTableColumns(tableName)
    columns = columns[1:-1]
    
    for i in range(0, len(columns), 1):
        position = ''
        if i != ( len(columns)-1 ):
            position = "{} [ position = {} ], ".format(columns[i], i)
            
            
        else:
            position = "{} [ position = {} ]".format(columns[i], i)
            
        string += position
        
    return string

         
def specialUploadToDatabase(file, myMap, column_info):
    groupID = myMap.get('groupID')
    tableName = myMap.get('tableName')
    
    columnHeaders = DBClient.getTableColumns(tableName)
    
    columnName = column_info[0][0]
    dt = column_info[0][1]
    
    df = pd.read_csv(file)
    
    if myMap.get('subjectPerCol') is True:
        df = Helper.transposeDataFrame(df, True)
    
    numpyArray = df.to_numpy()
    print(numpyArray)
    print('YO WHY')
    print(columnName)
    try:
        print('IN TRY')
        myDf = pd.DataFrame(columns=[columnName, 'subject_id']) 
        print('PAST MY DF')
        print(myDf)
        with transaction.atomic():
            print('IN ATOMIC!')
            
            i = 0
            for row in numpyArray:
                                
                subject_number = i 
        
                if myMap.get('hasSubjectNames') is True:
                    subject_number = row[0]
                    row = row[1:]
        
                subject_id, noError = DBHandler.subjectHandler("", groupID, subject_number)

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
                
                DBClient.dfInsert(tmpDf, tableName)
                i += 1
                
            print('ALL DONE')
    except:
        return False
    
    return True
    
    
    
def uploadToDatabase(file, filename, myMap, column_info, organizedColumns):
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
        listOfSubjects = []
        listOfSubjectNum = []
        
        if columnFlag is True:
            listOfSubjectNum = list(df.index)
        else:
            listOfSubjectNum = list(df.iloc[:,0])
        
        for num in listOfSubjectNum:
            if isinstance(num, str):
                num = num.upper()
                
            currID, errorMessage = DBHandler.subjectHandler("", groupID, num)
            listOfSubjects.append(currID)
        
        
        df = df.drop(df.columns[0], axis=1) # deleting the subjects column
        
        df = df[organizedColumns]
        df['subject_id'] = listOfSubjects
        
    else:
        subjectID, errorMessage = DBHandler.subjectHandler(filename, groupID)
        
        df = df[organizedColumns]
        df['subject_id'] = subjectID
        
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