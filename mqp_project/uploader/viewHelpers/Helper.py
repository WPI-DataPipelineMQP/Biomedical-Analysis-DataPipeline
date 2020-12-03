from datetime import datetime 
from ..models import Document  
import csv, os

import random

def pathIsBroken(session, uploadInfoFlag=False):
 
    if session.get('studyName', None) != None:
        print('Found StudyName')
        if uploadInfoFlag is True:
            print('Testing uploadInfoFlag')
            if session.get('uploaderInfo', None) != None:
                return False 
            
            else:
                return True 
            
        return False 

    
    return True


def deleteAllDocuments():
    filenames = Document.objects.all()
    
    for name in filenames:
        name.uploadedFile.delete()
        name.delete()


def clearUploadInfo(session):
    if session.get('uploaderInfo', None) != None:
        del session['uploaderInfo']


def clearStudyName(session):
    if session.get('studyName', None) != None:
        del session['studyName']
       
        
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
    print(string)
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
        

def hasHeaders(filepath):
    hasHeaders = False 
    with open(filepath, 'r') as csvfile:
        sniffer = csv.Sniffer()
        hasHeaders = sniffer.has_header(csvfile.read(2048))
        

    
    print(hasHeaders)
    return hasHeaders 

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
    
    print(filesLeft)
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
    
    
        
