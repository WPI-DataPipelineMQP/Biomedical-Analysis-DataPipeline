from datetime import datetime 
from .database import DBClient, DBHandler 

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
            
    cleanAttributeFormat = seperateByName(myExtras, 4)
            
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


def clean(columns):
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

            
def seperateByName(myList, flag):
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
    
    result = clean(columns)
    
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