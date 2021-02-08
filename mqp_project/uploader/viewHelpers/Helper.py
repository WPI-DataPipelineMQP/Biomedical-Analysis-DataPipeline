from django.core.files.storage import default_storage

from datapipeline.models import Attribute, DataCategory
from datapipeline.database import DBClient

from datetime import datetime  
from dateutil.parser import parse
import pandas as pd 
import csv, os, re

import random

"""Function verifies that user is not jumping around pages when navigating through uploader

PARAMS:
session - the request session in dictionary data structure 
uploadInfoFlag - a boolean to decide whether to check if the uploaderInfo stucture exists within the session

LOGIC:
if studyName is not in the session it means a incorrect jump was made so return False. Same concept applies 
if checking for the 'uploaderInfo' key existing in the session

returns Boolean - True if it detected that user tried going to a page they should not be accessing
"""
def pathIsBroken(session, uploadInfoFlag=False):
 
    if session.get('studyName', None) != None:
        if uploadInfoFlag is True:
            if session.get('uploaderInfo', None) != None:
                return False 
            
            else:
                return True 
            
        return False 

    
    return True


"""Function will delete the file with the provided filepath

filepath - a string of the filepath of the file to be deleted

returns None
"""
def deleteFile(filepath):
    os.remove(filepath)


"""Function that deletes all the documents in the uploaded_csv folder

LOGIC:
- iterate through each csv file (ignoring the .gitignore file) and delete it

returns None
"""
def deleteAllDocuments():
    
    directory_path = 'uploaded_csvs/'
    
    uploadedFiles = os.listdir(directory_path)
    
    for file in uploadedFiles:
        if file.endswith('.csv'):
            filepath = directory_path + file
            os.remove(filepath)
        
"""Function that removes uploaderInfo key from the session

PARAMS:
session - the request session to delete the key from

returns None 
"""
def clearKeyInSession(session, key):
    if session.get(key, None) != None:
        del session[key]


"""Function to return the value of 'SpecialCase' in the uploaderInfo dictionary (if exists)

PARAMS:
session - the request session to get the uploaderInfo from

returns Boolean - the value of SpecialCase or False if uploaderInfo is not in the session
"""       
def checkForSpecialCase(session):
    uploaderInfo = session.get('uploaderInfo')
    
    if uploaderInfo.get('SpecialCase', None) != None:
        return uploaderInfo.get('SpecialCase')
    
    return False
       
       
"""Function to extract the actual column names from a form POST request

PARAMS:
string - a string value of the raw column name to extract the name from

LOGIC:
- finds the index of the first occurance of '_' in the string 
- obtains the name from getting a substring of the string from 0 to the found index

returns String - the actual name of the column
"""       
def extractName(string):
    indexPos = string.find('_')
    
    name = string[:indexPos]
    
    return name 


"""Function to extract the field name from a form POST request

PARAMS:
string - a string value of the raw column name to extract the field name from

LOGIC:
- finds the index of the last occurance of '_' in the string 
- obtains the name from getting a substring of the string from the index after found index to the end of string

returns String - the field name
"""  
def getFieldName(string):
    indexPos = string.rfind('_')
    
    name = string[(indexPos+1):]
    
    return name


"""Function to organize the raw extras from the form to a list of tuples with the column name and its value in a tuple 

ex: [ (column1, value), (column2, value), ... ]

PARAMS:
myList - a list of the raw extras from the form

LOGIC:
- only perform the logic on column names that contains '_custom_dataType'
- if check is True, extract the value and the actual column name, put them into a tuple and add to the list

returns List - a clean list to easily parse through and get the necessary information from
""" 
def organizeExtraColsDataType(myList):
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
        '3' : 'NUMERIC(10,5)',
        '4' : 'DATETIME',
        '5' : 'BOOLEAN'
    }
    
    return dataTypeMap.get(string)


def convertToIntValue(string):
    dataTypeMap = {
        'TEXT': 1,
        'INT': 2,
        'NUMERIC(10,5)': 3,
        'DATETIME': 4,
        'BOOLEAN': 5
    }
    
    return dataTypeMap.get(string)


"""Function produces a nested dictionary so that each column will point to a dictionary of the fields corressponding to that column

ex: {
    'column1':
        {
            'field1': val,
            'field2': val
        }
    }
    
PARAMS:
columns - a list of the raw columns from the form
keepOriginal - boolean value that determines if the column name should stay the same (with the included spaces in between words)


returns Dictionary - a clean way to parse through the columns and their respective field values
"""
def clean(columns, keepOriginal):
    myMap = {}
    
    for column in columns:
        columnName = extractName(column[0][0])
        
        if keepOriginal is False:
            columnName = columnName.replace(" ", "")
            
        currMap = {}
        for field in column:
            fieldName = getFieldName(field[0])
            value = field[1]
            
            if fieldName == 'dataType':
                value = getActualDataType(field[1])
            
            currMap[fieldName] = value
            
        myMap[columnName] = currMap
    
    return myMap 


def reorderColsByPosition(result):
    numOfKeys = len(result.keys())
    
    orderedByPosition = []
    
    for key in result:
        index = int(result.get(key).get('position'))
        
        orderedByPosition.insert(index, key)
        
    return orderedByPosition

"""Function does the whole process of taking in raw inputs from the form and organizing it in the format that is produced from the clean function (look above)

PARAMS:
- myList - a raw list of tuples of the data gathered from the form
- flag - a int value to decide when to move on to next column. Say if there are 4 fields for each column, flag should be 4
    - will be used for iterating through myList. Iterate by the value of flag
    
- keepOriginal - boolean value that determines if the column name should stay the same (with the included spaces in between words)


return Dictionary (output of clean function)
"""          
def seperateByName(myList, flag, keepOriginal, retrieveAttribute, dcID):

    columns = [] # will be a 2D array (number of columns x value of flag)

    for i in range(0, len(myList), flag):
        currentList = myList[i:i+flag]
        columns.append(currentList)
    
    result = clean(columns, keepOriginal)
    
    if retrieveAttribute: 
        orderedCols = reorderColsByPosition(result)
        
        query = DataCategory.objects.filter(data_category_id=dcID)
        tableName = query[0].dc_table_name 
        
        tableCols = DBClient.getTableColumns(tableName)[1:-2]
        
        for i in range(0, len(orderedCols), 1):
            key_name = orderedCols[i] 
            inner_dict = result.get(key_name)
            
            attributeObj = Attribute.objects.filter(attr_name=tableCols[i], data_category=dcID) 
            attributeObj = attributeObj[0]
            attributeType = attributeObj.data_type
        
            inner_dict['dataType'] = attributeType
        
            result[key_name] = inner_dict

            
    return result         
       
            
def foundDuplicatePositions(myMap):
    foundPositions = set()
    
    for key in myMap:
        currDict = myMap.get(key)
        currPos = currDict.get('position')
        
        if currPos in foundPositions:
            return True
        
        else:
            foundPositions.add(currPos)
            
    return False


def getDatetime(string):
    dateObj = datetime.strptime(string, '%Y-%m-%d').date()
    
    return dateObj


def validDates(start, end):
    if start <= end:
        return True 
    
    return False


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


def modifyFileName(name):
    modifiedResult = name
    
    underLineIndex = name.find('_')
    
    if underLineIndex != -1:
        latterHalf = name[underLineIndex:]
        
        subject_number = name[:underLineIndex]
        
        subject_number = subject_number.upper() 
        
        modifiedResult = subject_number + latterHalf
        
    return modifiedResult
        

def hasDate(string):
    try:
        parse(string)
        return True 
    
    except ValueError:
        return False 
    
        
def hasAcceptableHeaders(filepath):
    df = pd.read_csv(filepath)
    
    unnamedCols = any(col == True for col in df.columns.str.contains('^Unnamed'))
    
    if unnamedCols:
        return False 
    
    for header in list(df.columns):
        if hasDate(header):
            return False 
        
        if header.isnumeric():
            return False 
        
    
    return True


def extractHeaders(path, subjectOrgVal):
    df = pd.read_csv(path) 
    
    hasSubjectNames = False 
    subjectPerCol = False 
    
    if subjectOrgVal == 'column':
        subjectPerCol = True 
        hasSubjectNames = True
        df = transposeDataFrame(df, False)
        
    headers = list(df.columns)
    
    headers = [col.lower().replace(' ', '') for col in headers]
    
    return headers, hasSubjectNames, subjectPerCol


def transposeDataFrame(df, withSubjects=True):
    indexVal = df.columns[0] # used to maintain labels after transposing
    
    df_t = df.set_index(indexVal).T # transposing the matrix 
    
    subjects = list(df_t.index) 
    
    if withSubjects is True:
        df_t.insert(loc=0, column='Subjects', value=subjects)

    
    return df_t   

def replaceWithNameOfValue(extras, name):
    newExtras = []
    for i, item in enumerate(extras):
        itemName = item[0]
        itemValue = item[1]
        newName = itemName.replace('Entered Name', name)
        newExtras.append( (newName, itemValue) )
        
    return newExtras


def getUploadResults(filenames):
    directory_path = 'uploaded_csvs/'
    
    filesLeft = os.listdir(directory_path)
    
    filesLeft.remove('.gitignore')
    
    if len(filesLeft) == 0:
        return filenames, ['none'] 
    
    filesUploaded = []
    
    for file in filenames:
        if file in filesLeft:
            continue 
        
        filesUploaded.append(file)
        
    if len(filesUploaded) == 0:
        filesUploaded.append('none')
        
    return filesUploaded, filesLeft 


def getFieldsFromInfoForm(uploaderForm, files):
    fields, filenames = {}, []
    
    for field in uploaderForm.fields:
        if uploaderForm.cleaned_data[field]:
            if field == 'uploadedFiles':
                path = 'uploaded_csvs/'
                for file in files:
                    filepath = path + file.name
                    filenames.append(file.name)
                    default_storage.save(filepath, file)
                            
                        
            else:
                fields[field] = uploaderForm[field].data
                
    return fields, filenames

def cleanCategoryName(name):
    
    name = re.sub(r'[^A-Za-z0-9]+', '', name)
    
    print(name)
        
    return name

def passFilenameCheck(files):
    for file in files:
        if file.find('_') == -1:
            return False 
        
        else:
            if len(file[:file.find('_')]) <= 0:
                return False 
            
    return True
    
    
        
