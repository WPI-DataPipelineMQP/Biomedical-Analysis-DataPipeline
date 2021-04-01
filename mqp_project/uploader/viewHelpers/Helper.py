from django.core.files.storage import default_storage

from datapipeline.models import Attribute, DataCategory
from datapipeline.database import DBClient
from django.conf import settings

from datetime import datetime  
from dateutil.parser import parse
from io import StringIO
import pandas as pd 
import csv, os, re

import boto3 

import random


###
# Description: verifies that user is not jumping around pages when navigating through uploader
# PARAMS: session (dictionary), uploadInfoFlag (boolean)
# RETURN: Boolean - True if it detected that user tried going to a page they should not be accessing 
###
def pathIsBroken(session, uploadInfoFlag=False):
 
    if session.get('studyName', None) != None:
        if uploadInfoFlag is True:
            if session.get('uploaderInfo', None) != None:
                return False 
            
            else:
                return True 
            
        return False 

    
    return True

###
# Description: gets all the keys in the AWS S3 Bucket
# RETURN: List - a list of all the keys in the bucket
###
def getAllKeysInS3():
    s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    
    keys = [file.key for file in bucket.objects.all()]
    
    return keys

    
###
# Description: deletes all the documents in the S3 Bucket. Goal is so we can keep the free plan :)
# RETURN: None
###
def deleteAllDocuments():
    s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    
    for file in bucket.objects.all():
        key = file.key
        
        s3.Object(settings.AWS_STORAGE_BUCKET_NAME, key).delete()
  
      
###
# Description: deletes a specific file in the S3 Bucket
# PARAM: file (String) [name of the file]
# RETURN: None
###
def deleteFile(file):
    s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME 
    key = 'uploaded_csvs/' + file
    s3.Object(bucket_name, key).delete()
    
        
        
###
# Description: removes a key and value from session dictionary
# PARAMS: session (dictionary), key (String)
# RETURN: None
###
def clearKeyInSession(session, key):
    if session.get(key, None) != None:
        del session[key]


###
# Description: checks to see if the uploaderInfo contains the 'SpecialCase' key in the dictionary 
# PARAMS: session (dictionary)
# RETURN: Boolean - returns the value of SpecialCase of False if the key was not in the session  
###
def checkForSpecialCase(session):
    uploaderInfo = session.get('uploaderInfo')
    
    if uploaderInfo.get('SpecialCase', None) != None:
        return uploaderInfo.get('SpecialCase')
    
    return False
       
       
###
# Description: extracts the column name from a form POST request
# PARAMS: string ( string )
# RETURN: String - the name  
###    
def extractName(string):
    indexPos = string.find('_')
    
    name = string[:indexPos]
    
    return name 


###
# Description: extracts the field name from a form POST request
# PARAMS: string (string)
# RETURN: String - the field name
def getFieldName(string):
    indexPos = string.rfind('_')
    
    name = string[(indexPos+1):]
    
    return name


###
# Description: organizes the raw extras from the form to a list of tuples with the column name and its value in a tuple
# PARAMS: myList (list of tuples) ex: [ (column1, value), (column2, value), ... ]
# RETURN: List - a clean list to easily parse through and get the necessary information from
def organizeExtraColsDataType(myList):
    clean = []
    for (name, val) in myList:
        if '_custom_dataType' in name:
            colName = extractName(name)
            colName = colName.replace(" ", "")
            clean.append((colName, val))
    
    return clean


###
# Description: gets the corresponding PostgreSQL Datatype depending on the value that is passed in
# PARAMS: string (string)
# RETURN: String - the corresponding PostgreSQL datatype 
###
def getActualDataType(string):
    dataTypeMap = {
        '1' : 'TEXT',
        '2' : 'INT',
        '3' : 'NUMERIC(10,5)',
        '4' : 'DATETIME',
        '5' : 'BOOLEAN'
    }
    
    return dataTypeMap.get(string)

###
# Description: gets the corresponding PostgreSQL Datatype integer value based on the getActualDataType function map
# PARAMS: string (string)
# RETURN: String - the corresponding PostgreSQL datatype integer value
###
def convertToIntValue(string):
    dataTypeMap = {
        'TEXT': 1,
        'INT': 2,
        'NUMERIC(10,5)': 3,
        'DATETIME': 4,
        'BOOLEAN': 5
    }
    
    return dataTypeMap.get(string)


###
# Description: produces a nested dictionary so that each column will point to a dictionary of the fields corresponding to that column
# PARAMS: columns (list), keepOriginal (Boolean)
# RETURN: Dictionary - a clean way to parse through the columns and their respective field values
# {
#     'column1':
#         {
#             'field1': val,
#             'field2': val
#         }
# }
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


###
# Description: reorders the columns to their correct position within the database table
# PARAMS: result (dictionary)
# RETURN: List - the proper ordering of the columns according to the corresponding database table
def reorderColsByPosition(result):
    numOfKeys = len(result.keys())
    
    orderedByPosition = []
    
    for key in result:
        index = int(result.get(key).get('position'))
        
        orderedByPosition.insert(index, key)
        
    return orderedByPosition

         
###
# Description: takes in the raw inputs from the form and organizes it into the format that is produced from the clean function
# PARAMS: myList (List of tuples), flag (Integer), keepOriginal (Boolean), retrieveAttribute (Boolean), dcID (Integer)
# RETURN: Dictionary - look at the clean function
###
def seperateByName(myList, flag, keepOriginal, retrieveAttribute, dcID):

    columns = [] # will be a 2D array (number of columns x value of flag)
    
    # flag is used to decide when to move on to the next column. Say if there are 4 fields for each column, flag should be 4
    for i in range(0, len(myList), flag):
        currentList = myList[i:i+flag]
        columns.append(currentList)
    
    result = clean(columns, keepOriginal)
    
    # does some extra stuff when retrieving the attributes (basically just gets the data type from the Attribute Database Table)
    if retrieveAttribute: 
        orderedCols = reorderColsByPosition(result)
        
        query = DataCategory.objects.filter(data_category_id=dcID)
        tableName = query[0].dc_table_name 
        
        tableCols = DBClient.getTableColumns(tableName)[1:-2]
        
        if len(orderedCols) != len(tableCols):
            print('Mismatch')
            return None 
        
        for i in range(0, len(orderedCols), 1):
            key_name = orderedCols[i] 
            inner_dict = result.get(key_name)
            
            attributeObj = Attribute.objects.filter(attr_name=tableCols[i], data_category=dcID) 
            attributeObj = attributeObj[0]
            attributeType = attributeObj.data_type
        
            inner_dict['dataType'] = attributeType
        
            result[key_name] = inner_dict

            
    return result         
       

###
# Description: checks if the user entered in duplicate positions 
# PARAMS: myMap (Dictionary)
# RETURN: Boolean - True if duplicate position was detected
###
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


###
# Description: gets the datetime object of the entered in date (this is in String form)
# PARAMS: string (String)
# RETURN: Datetime
###
def getDatetime(string):
    dateObj = datetime.strptime(string, '%Y-%m-%d').date()
    
    return dateObj


###
# Description: checks if the end date is before the start date
# PARAMS: start (Datetime), end (Datetime)
# RETURN: Boolean - True if the start date is before the end date
###
def validDates(start, end):
    if start <= end:
        return True 
    
    return False


###
# Description: gets all the column information and organizes the columns to allow the data to be uploaded to the db successfully
# PARAMS: positionInfo (Dictionary)
# RETURN: Tuple - (List of tuple, List of String)
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

###
# Description: modifies the subject names to be in all caps (makes things easier to query [at least at the state that it is in right now])
# PARAMS: name (String)
# RETURN: String - modified name with the subject name in all caps
###
def modifyFileName(name):
    modifiedResult = name
    
    underLineIndex = name.find('_')
    
    if underLineIndex != -1:
        latterHalf = name[underLineIndex:]
        
        subject_number = name[:underLineIndex]
        
        subject_number = subject_number.upper() 
        
        modifiedResult = subject_number + latterHalf
        
    return modifiedResult
        

###
# Description: checks if there is a date within the string
# PARAM: string (String)
# RETURN: Boolean - True if it found a date in the string
###
def hasDate(string):
    try:
        parse(string)
        return True 
    
    except ValueError:
        return False 

###
# Description: gets the dataframe of the csv file that was uploaded in the AWS S3 Bucket
# PARAMS: filename (String)
# RETURN: Dataframe - the data frame of the corresponding csv file stored in the S3 Bucket
###
def getDataFrame(filename):
    filename = "uploaded_csvs/" + filename
    client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME 
    
    try: 
        csv_obj = client.get_object(Bucket=bucket_name, Key=filename)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
    
        df = pd.read_csv(StringIO(csv_string)) 
    
        return df
    
    except:
        return None
    
###
# Description: checks if the csv file has acceptable headers (no unnamed columns, columns containing dates, or columns containing numbers)
# PARAMS: df (DataFrame)
# RETURN: Boolean - True if the csv file has acceptable headers
###
def hasAcceptableHeaders(df):
    
    unnamedCols = any(col == True for col in df.columns.str.contains('^Unnamed'))
    
    if unnamedCols:
        return False 
    
    for header in list(df.columns):
        if hasDate(header):
            return False 
        
        if header.isnumeric():
            return False 
        
    
    return True

###
# Description: gets the header names and makes any necessary modifications to them if needed
# PARAMS: df (Dataframe), subjectOrgVal (String)
# RETURN: Tuple - (list of string, Boolean, Boolean)
###
def extractHeaders(df, subjectOrgVal):
    
    hasSubjectNames = False 
    subjectPerCol = False 
    
    if subjectOrgVal == 'column':
        subjectPerCol = True 
        hasSubjectNames = True
        df = transposeDataFrame(df, False)
        
    headers = list(df.columns)
    
    regex = re.compile('[^a-zA-Z ]')
    headers = [regex.sub('', col).lower() for col in headers]
    
    return headers, hasSubjectNames, subjectPerCol


###
# Description: does a transpose on the provided dataframe 
# PARAMS: df (Dataframe), withSubjects (Boolean)
# RETURN: the transpose version of the inputted dataframe
###
def transposeDataFrame(df, withSubjects=True):
    indexVal = df.columns[0] # used to maintain labels after transposing
    
    df_t = df.set_index(indexVal).T # transposing the matrix 
    
    subjects = list(df_t.index) 
    
    if withSubjects is True:
        df_t.insert(loc=0, column='Subjects', value=subjects)

    
    return df_t   


###
# Description: instead of reading the header from the csv, it allows the user to add in their on column name.
#    This is used for if the file is subject by row and is time series since this file does not expect there to be a header included
# PARAMS: extras (list of tuples), name (String)
# RETURN: List of Tuples
###
def replaceWithNameOfValue(extras, name):
    newExtras = []
    for i, item in enumerate(extras):
        itemName = item[0]
        itemValue = item[1]
        newName = itemName.replace('Entered Name', name)
        newExtras.append( (newName, itemValue) )
        
    return newExtras

###
# Description: looks at what is left in the AWS S3 Bucket to see which files were uploaded successfully and those that were not
# PARAMS: filenames (List of String)
# RETURN: Tuple - (List of String, List of String)
###
def getUploadResults(filenames):

    raw_files = getAllKeysInS3()
    filesLeft = []
    for file in raw_files:
        index = file.index('/')
        filesLeft.append(file[index+1:])
        
    
    if len(filesLeft) == 0:
        return filenames, ['none'] 
    
    filesUploaded = []
    
    for file in filenames:
        if file not in filesLeft:
            filesUploaded.append(file)
        
    if len(filesUploaded) == 0:
        filesUploaded.append('none')
        
    return filesUploaded, filesLeft 


###
# Description: gets the raw results from the form and organizes the fields into a dictionary and the filenames into a list
# PARAMS: uploaderForm (Django Form), files (List of Files)
# RETURN: Tuple - (Dictionary of the Fields, List of the Filenames)
###
def getFieldsFromInfoForm(uploaderForm, files):
    fields, filenames = {}, []
    
    for field in uploaderForm.fields:
        if uploaderForm.cleaned_data[field]:
            if field == 'uploadedFiles':
                path = settings.UPLOAD_PATH
                for file in files:
                    
                    filenames.append(file.name)
                    filepath = "uploaded_csvs/" + file.name
                    default_storage.save(filepath, file)
                        
            else:
                fields[field] = uploaderForm[field].data
                
    return fields, filenames

###
# Description: makes the category name acceptable to be a name of a database table
# PARAMS: name (String)
# RETURN: String - a cleaned version of the provided name
###
def cleanCategoryName(name):
    
    name = re.sub(r'[^A-Za-z0-9]+', '', name)
        
    return name


###
# Description: checks to see if the filename contains a "_" character and has text before the "_"
# PARAMS: files (List of String)
# RETURN: Boolean - True if all the filenames follow the proper naming convention
###
def passFilenameCheck(files):
    for file in files:
        if file.find('_') == -1:
            return False 
        
        else:
            if len(file[:file.find('_')]) <= 0:
                return False 
            
    return True
    
    
        
