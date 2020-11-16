from datetime import datetime 
from .database import DBClient, DBHandler 
import pandas as pd 
import numpy as np

import random

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
            
    myMap = DBHandler.dataCategoryHandler(myMap, studyID)
            
    uploaderInfo['tableName'] = myMap.get('tableName')
    uploaderInfo['dcID'] = myMap.get('DC_ID')
            
    cleanResult = getCleanFormat(myExtras)
            
    if subjectRule == 'row' and isTimeSeries == 'y':
        columnName = myFields.get('nameOfValueMeasured')
        columnVal = myFields.get('datatypeOfMeasured') 
        cleanResult = [(columnName, columnVal)] 
        uploaderInfo['headerInfo'] = [columnName]
        
            
    myMap['columns'] = cleanResult
            
    DBHandler.newTableHandler(myMap)
            
    cleanAttributeFormat = seperateByName(myExtras, 4, False)
            
    DBHandler.insertToAttribute(cleanAttributeFormat, myMap.get('DC_ID'))
    
    return uploaderInfo


def extractName(string):
    indexPos = string.find('_')
    
    name = string[:indexPos]
    
    return name 


def getFieldName(string):
    indexPos = string.rfind('_')
    
    name = string[(indexPos+1):]
    
    return name


def getCleanFormat(myList):
    clean = []
    for (name, val) in myList:
        if '_custom_dataType' in name:
            colName = extractName(name)
            colName = colName.replace(" ", "")
            clean.append((colName, val))
    
    return clean

def getActualDataType(string):
    dataTypeMap = {
        '1' : 'TEXT',
        '2' : 'INT',
        '3' : 'FLOAT(10,5)',
        '4' : 'DATETIME',
        '5' : 'BOOLEAN'
    }
    
    return dataTypeMap.get(string)

def convertToIntValue(string):
    dataTypeMap = {
        'TEXT': 1,
        'INT': 2,
        'FLOAT(10,5)': 3,
        'DATETIME': 4,
        'BOOLEAN': 5
    }
    
    return dataTypeMap.get(string)

def clean(columns, keepOriginal):
    myMap = {}
    dataTypeMap = {
        '1' : 'TEXT',
        '2' : 'INT',
        '3' : 'FLOAT(10,5)',
        '4' : 'DATETIME',
        '5' : 'BOOLEAN'
    }
    
    for column in columns:
        columnName = extractName(column[0][0])
        
        if keepOriginal is False:
            columnName = columnName.replace(" ", "")
            
        currMap = {}
        for field in column:
            fieldName = getFieldName(field[0])
            value = field[1]
            
            if fieldName == 'dataType':
                value = dataTypeMap.get(field[1])
            
            currMap[fieldName] = value
            
        myMap[columnName] = currMap
    
    return myMap 

            
def seperateByName(myList, flag, keepOriginal):
    index = 0
    i = 0
    
    columns = []
    currentList = []
    while index < len(myList):
        if i < flag:
            currentList.append(myList[index])
            i += 1
            
        if i == flag:
            columns.append(currentList)
            currentList = [] 
            i = 0
        
        index += 1
    
    result = clean(columns, keepOriginal)
    
    return result         
       
            
def foundDuplicatePositions(myMap):
    foundPositions = {}
    
    for key in myMap:
        currDict = myMap.get(key)
        currPos = currDict.get('position')
        
        if currPos in foundPositions.keys():
            return True
        
        else:
            foundPositions[currPos] = 0
            
    return False


def getDatetime(string):
    dateObj = datetime.strptime(string, '%Y-%m-%d').date()
    
    return dateObj


def validDates(start, end):
    if start <= end:
        return True 
    
    return False


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
            
    
def getInfo(positionInfo):
    organizedColumns = [''] * len(positionInfo)
    columnInfo = []
    
    for key in positionInfo.keys():
        currDict = positionInfo.get(key)
        
        position = int(currDict.get('position'))
        tmpDT = currDict.get('dataType')
        dataType = convertToIntValue(tmpDT)
        
        organizedColumns[position] = key 
        columnInfo.append( (key, dataType) )
        
    
    return columnInfo, organizedColumns

def specialUploadToDatabase(file, myMap, column_info):
    groupID = myMap.get('groupID')
    tableName = myMap.get('tableName')
    
    columnHeaders = DBClient.getTableColumns(tableName)
    
    columnName = column_info[0][0]
    dt = column_info[0][1]
    
    df = pd.read_csv(file)
    
    numpyArray = df.to_numpy()
    
    for i, row in enumerate(numpyArray):
        subject_number = i 
        
        if myMap.get('hasSubjectNames') is True:
            subject_number = row[0]
            row = row[1:]
        
        subject_id = DBHandler.subjectHandler("", groupID, subject_number)
        
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
    
    
    
def uploadToDatabase(file, myMap, column_info, organizedColumns, subjectID=None):
    df = pd.read_csv(file)
    
    groupID = myMap.get('groupID')
    tableName = myMap.get('tableName')
    
    df = df[organizedColumns]
    
    if myMap.get('hasSubjectNames') is True:
        listOfSubjects = []
        
        listOfSubjectNum = df[[df.columns[0]]].tolist()
        
        for num in listOfSubjectNum:
            currID = DBHandler.subjectHandler("", groupID, num)
            listOfSubjectNum.append(currID)
            
        
        df['subject_id'] = listOfSubjectNum
        
    else:
        numOfRows = len(df.index)
        
        subject_number = random.sample(range(numOfRows), 1)[0]
        
        if subjectID is None:
            subjectID = DBHandler.subjectHandler("", groupID, subject_number)
            
        df['subject_id'] = subjectID
        
    
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
    
    if len(columnHeaders) > 0:
        columnHeaders = columnHeaders[1:]
        
        df.columns = columnHeaders
        
        DBClient.dfInsert(df, tableName)
        
    else:
        print('FOUND ERROR IN COLUMNS')
        
        
        
    
    