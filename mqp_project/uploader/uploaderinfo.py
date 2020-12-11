from django.db import IntegrityError, DatabaseError, transaction
from datapipeline.database import DBClient
from datapipeline.models import Study, StudyGroup, Subject, DataCategory, DataCategoryStudyXref
from .models import Document

from uploader.viewHelpers import Helper, DBFunctions

import pandas as pd 
import numpy as np

class UploaderInfo:
    def __init__(self, studyName):
        self.studyName = studyName
        self.groupName = ''
        self.categoryName = ''
        self.subjectOrganization = ''
        self.isTimeSeries = False 
        self.handleDuplicate = ''
        self.specialCase = False 
        self.headers = []
        self.tableName = ''
        self.hasSubjectNames = False 
        self.studyID = -1
        self.dcID = -1
        self.groupID = -1
        self.uploadedFiles = []
        self.subjectPerCol = False
        self.specialInsert = '' 
        
    
    def getAllAttributes(self):
        
        return self.__dict__
        
        
    def documentExists(self, filename):
        
        document_dcID = DBFunctions.getDataCategoryIDIfExists(self.categoryName, self.isTimeSeries, self.studyID)
        
        if document_dcID != -1:
            dcObj = DataCategory.objects.get(data_category_id=document_dcID) 
            exists = Document.objects.filter(filename=filename, data_category=dcObj).exists()
            
            return exists 
        
        return False
    
    
    def updateFieldsFromDataCategory(self, dcID):
        self.tableName = (DataCategory.objects.get(data_category_id=dcID)).dc_table_name
        self.isTimeSeries = (DataCategory.objects.get(data_category_id=dcID)).is_time_series
        self.hasSubjectNames = (DataCategory.objects.get(data_category_id=dcID)).has_subject_name
        
        
    def dataCategoryHandler(self, myMap):
        
        errorMessage = None
        description = myMap.get('DC_description')
        
        insertSuccess, errorMessage = DBFunctions.insertToDataCategory(self.categoryName, self.isTimeSeries, self.hasSubjectNames, self.tableName, description)
    
        if insertSuccess is False:
            return False, errorMessage
    
        data_category_id = DBFunctions.getDataCategoryID(self.tableName, self.isTimeSeries)
        
        self.dcID = data_category_id
        insertSuccess, errorMessage = DBFunctions.insertToDataCategoryXref(data_category_id, self.studyID)

        if insertSuccess is False:
            return False, errorMessage

        return True, ''

    
    def __performTransaction(self, myMap, myExtras):
        
        errorMessage = ''
        
        data_category_name = self.categoryName.replace(" ", "_")
        attachmentToTableName = f'_{self.studyID}'
        self.tableName = data_category_name + attachmentToTableName
        myMap['tableName'] = self.tableName
        
        # do this first because MySQL does not support DDL transactions
        noErrors, errorMessage = DBFunctions.createNewTable(myMap)
                
        if noErrors is False:
            raise DatabaseError(errorMessage)
        
        noErrors, errorMessage = self.dataCategoryHandler(myMap) 
                
        if noErrors is False:
            DBFunctions.dropTable(self.tableName)
            raise DatabaseError(errorMessage)
                
        cleanAttributeFormat = Helper.seperateByName(myExtras, 4, False)
                
        noErrors, errorMessage = DBFunctions.insertToAttribute(cleanAttributeFormat, self.dcID)
                
        if noErrors is False:
            DBFunctions.dropTable(self.tableName)
            raise DatabaseError(errorMessage)
        
        
        
    def handleMissingDataCategoryID(self, subjectRule, otherInfo):
        
        myFields, myExtras = otherInfo[0], otherInfo[1]
        
        subjectVal = myFields.get('hasSubjectID')
        
        self.hasSubjectNames = True if subjectVal == 'y' else False        
            
        myMap = {
            'categoryName': self.categoryName,
            'isTimeSeries': self.isTimeSeries,
            'hasSubjectNames': self.hasSubjectNames,
            'DC_description': myFields.get('dataCategoryDescription'),
            'columns': Helper.organizeExtraColsDataType(myExtras),
            'createTable': False
        }
        
        try:
            with transaction.atomic():
                self.__performTransaction(myMap, myExtras)
                 
        except DatabaseError as e:
            print('SHOULD ROLLBACK')
            return str(e)
        
        return None
         
    
    
    def subjectHandler(self, filename, subjectNumber=None):
        subject_number = subjectNumber
        
        if subjectNumber is None:
            subject_number = filename.split('_')[0] 
            
        subject_id = DBFunctions.getSubjectID(subject_number, self.groupID)
        
        if subject_id == -1:
            insertSuccess = DBFunctions.insertToSubject(subject_number, self.groupID)
            
            if insertSuccess is False:
                errorMessage = 'ERROR: Error Found When Attempting to Insert Subject_Number: {} and Study Group ID: {} to Subject Table'.format(subject_number, self.groupID)
                
                return -1, errorMessage
        
        subject_id = DBFunctions.getSubjectID(subject_number, self.groupID)
        
        return subject_id, None
    
    #private method
    def __adjustDFTypes(self, df, columnName, dt):
        
        if dt == 1:
            df[[columnName]].astype(str)

        elif dt == 2:
            df[[columnName]].astype(int)

        elif dt == 3:
            df[[columnName]].astype(float)
            
        elif dt == 4:
            df[columnName] = pd.to_datetime(df[columnName])
            df[columnName] = df[columnName].dt.strftime('%Y-%m-%d %H:%M:%S')
            
        else:
            df[columnName].astype(bool)
            
        return df  
    
    
    def specialUploadToDatabase(self, file, docID, column_info):
        
        columnHeaders = DBClient.getTableColumns(self.tableName)
        
        columnName = column_info[0][0]
        dt = column_info[0][1]
        
        df = pd.read_csv(file)
        
        if self.subjectPerCol is True:
            df = Helper.transposeDataFrame(df, True)
    
        numpyArray = df.to_numpy()

        try:
            myDf = pd.DataFrame(columns=[columnName, 'subject_id', 'doc_id']) 
            
            with transaction.atomic():
                for i, row in enumerate(numpyArray):
                    
                    subject_number = i 
        
                    if self.hasSubjectNames is True:
                        subject_number = row[0]
                        row = row[1:]
                        
                    subject_id, noError = self.subjectHandler("", subject_number)

                    if noError is False:
                        raise Exception()
        
                    tmpDf = pd.DataFrame(row, columns=[columnName])
                    
                    tmpDf = self.__adjustDFTypes(tmpDf, columnName, dt)
                    
                    tmpDf['subject_id'] = subject_id
                    
                    tmpDf['doc_id'] = docID
                
                    myDf = myDf.append(tmpDf, ignore_index=True)
                    
            DBClient.dfInsert(myDf, self.tableName)
            print('ALL DONE')
            
        except Exception as e:
            errorMessage = str(e)
            return False, errorMessage     
        
        return True, None
    
    
    def uploadToDatabase(self, filepath, filename, docID, column_info, organizedColumns):
        errorMessage = None
        columnFlag = False 
        
        df = pd.read_csv(filepath)
        
        if self.subjectPerCol is True:
            columnFlag = True
            df = Helper.transposeDataFrame(df, True)
            
        filename = Helper.modifyFileName(filename)
        
        if self.hasSubjectNames is True:
            listOfSubjects, listOfSubjectNum = [], []
            
            if columnFlag is True:
                listOfSubjectNum = list(df.index)
                
            else:
                listOfSubjectNum = list(df.iloc[:,0])
                
            for num in listOfSubjectNum:
                if isinstance(num, str):
                    num = num.upper()
                    
                currID, errorMessage = self.subjectHandler("", num)
                listOfSubjects.append(currID)
                
            df = df.drop(df.columns[0], axis=1) # deleting the subjects column
            df = df[organizedColumns]
            df['subject_id'] = listOfSubjects
        
        
        else:
            subjectID, errorMessage = self.subjectHandler(filename)
        
            df = df[organizedColumns]
            df['subject_id'] = subjectID
    
        df['doc_id'] = docID
        
        try:
            with transaction.atomic():
                for col in column_info:
                    col_name = col[0]
                    dt = col[1]
                    
                    df = self.__adjustDFTypes(df, col_name, dt)
                    
                columnHeaders = DBClient.getTableColumns(self.tableName)
                
                if len(columnHeaders) == 0:
                    errorMessage = "ERROR: found no column headers for {} table".format(self.tableName)
                    raise Exception()
            
                columnHeaders = columnHeaders[1:]
        
                df.columns = columnHeaders

                DBClient.dfInsert(df, self.tableName)
    
        except Exception as e:
            if errorMessage is None:
                errorMessage = str(e)
                
                return False, errorMessage     
    
        return True, None
    
    