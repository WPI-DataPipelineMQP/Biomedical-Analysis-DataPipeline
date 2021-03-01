from django.db import IntegrityError, DatabaseError, transaction
from datapipeline.database import DBClient
from datapipeline.models import Study, StudyGroup, Subject, DataCategory, DataCategoryStudyXref
from .models import Document

from uploader.viewHelpers import Helper, DBFunctions

import pandas as pd 
import numpy as np

'''
Purpose: Easy way to store all the data collected from the users and some way encapsulate the data
'''
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
        
    
    ###
    # Description: simply verifies if the uploaded file has already been uploaded by checking to see if the filename exsists in the Document table 
    # PARAMS: filename (string)
    # RETURN: Boolean - whether the file exists within the Document table in the database
    ###    
    def documentExists(self, filename):
        
        document_dcID = DBFunctions.getDataCategoryIDIfExists(self.categoryName, self.isTimeSeries, self.subjectOrganization, self.studyID)
        
        if document_dcID != -1:
            dcObj = DataCategory.objects.get(data_category_id=document_dcID) 
            exists = Document.objects.filter(filename=filename, data_category=dcObj).exists()
            
            return exists 
        
        return False
    
    
    ###
    # Description: updates the object fields based on what is stored within the DataCategory table
    # PARAMS: dcID (int) - the Data Category entry id to look at
    # RETURN: None
    ###
    def updateFieldsFromDataCategory(self, dcID):
        self.tableName = (DataCategory.objects.get(data_category_id=dcID)).dc_table_name
        self.isTimeSeries = (DataCategory.objects.get(data_category_id=dcID)).is_time_series
        self.hasSubjectNames = (DataCategory.objects.get(data_category_id=dcID)).has_subject_name
      
        
    ###
    # Description: checks to see if the data category name already exists within the DataCategory table
    # PARAMS: None
    # RETURN Boolean - True if the data category name along with other attributes already exists within the DataCategory table
    ###
    def isExistingDataCategory(self):
        res = DataCategory.objects.filter(data_category_name=self.categoryName, 
                                          is_time_series=self.isTimeSeries, 
                                          subject_organization=self.subjectOrganization).exists()
        
        return res
        
    
    ###
    # Description: method to handle the inserts into the DataCategory and DataCategoryStudyXref tables
    # PARAMS: description (string) - the description of the data category
    # RETURN: Boolean - True if the inserts have been successful
    ###
    def dataCategoryHandler(self, description):
        
        errorMessage = None
        
        insertSuccess, errorMessage = DBFunctions.insertToDataCategory(self.categoryName, self.isTimeSeries, self.hasSubjectNames, self.tableName, description, self.subjectOrganization)
    
        if insertSuccess is False:
            return False, errorMessage
    
        data_category_id = DBFunctions.getDataCategoryID(self.tableName, self.isTimeSeries)
        
        self.dcID = data_category_id
        insertSuccess, errorMessage = DBFunctions.insertToDataCategoryXref(data_category_id, self.studyID)

        if insertSuccess is False:
            return False, errorMessage

        return True, ''

    
    ###
    # Description: Puts the inserts to the DataCategory, DataCategoryStudyXref, and Attribute tables nto a transaction.
    #              By putting them in a transaction statement, it will allow a rollback to be performed if any errors occurred during the transaction
    # PARAMS: myMap (Dictionary), myExtras (List of tuples)
    # RETURN: None
    ###
    def __performTransaction(self, myMap, myExtras):
        
        errorMessage = ''
        
        noErrors, errorMessage = self.dataCategoryHandler(myMap.get('DC_description')) 
                
        if noErrors is False:
            DBFunctions.dropTable(self.tableName)
            raise DatabaseError(errorMessage)
        
        cleanAttributeFormat = Helper.seperateByName(myExtras, 4, False, False, self.dcID)
                
        noErrors, errorMessage = DBFunctions.insertToAttribute(cleanAttributeFormat, self.dcID)
                
        if noErrors is False:
            DBFunctions.dropTable(self.tableName)
            raise DatabaseError(errorMessage)
        
    
    ###
    # Description: defines the whole process of when adding a new Data Category
    # PARAMS: myFields (Dictionary), myExtras (List)
    # RETURN: String or None - String if an error occurred and it returns the error message
    ###    
    def handleMissingDataCategoryID(self, myFields, myExtras):
        
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
        
        data_category_name = self.categoryName.replace(" ", "_")
        attachmentToTableName = f'_{self.studyID}'
        self.tableName = data_category_name + attachmentToTableName
        self.tableName = self.tableName.lower()
        myMap['tableName'] = self.tableName
        
        noErrors, errorMessage = DBFunctions.createNewTable(myMap)
                
        if noErrors is False:
            return str(errorMessage)
            
        try:
            with transaction.atomic():
                self.__performTransaction(myMap, myExtras)
                 
        except DatabaseError as e:
            print('ROLLBACK OCCURED')
            return str(e)
        
        return None
         
    
    ###
    # Description: this method will always return a subjectID back to the user. If the subject does not exist within the Subject table
    #               a new subject is inserted into the table and that subjectID will be retrieved and returned
    # PARAMS: filename (string), subjectNumber (int)
    # RETURN: Integer - the subjectID of the targeted subject in the Subject table 
    ###
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
    
    
    ###
    # Description: makes sure that the column of the dataframe is of the correct data type
    # PARAMS: df (pandas dataframe), columnName (string), dt (int)
    # RETURN: DataFrame - the dataframe with the correct data type for the targeted column name 
    ###
    def __adjustDFTypes(self, df, columnName, dt):
        
        if dt == 1:
            df[[columnName]].astype(str)

        elif dt == 2:
            df[[columnName]].astype(int)

        elif dt == 3:
            df[[columnName]].astype(float)
            
        elif dt == 4:
            firstDateTime = df.iloc[0, df.columns.get_loc(columnName)]
            
            if firstDateTime.count(':') == 3:   # handles the datetime format HH:MM:SS:MS and converts it to HH:MM:SS
                df['reverse'] = df.loc[:,columnName].apply(lambda x: x[::-1])
                df['reverse'] = df['reverse'].str.replace(':', '.', 1)
                df[columnName] = df.loc[:,'reverse'].apply(lambda x: x[::-1])
                del df['reverse']
            
            df[columnName] = pd.to_datetime(df[columnName])
            df[columnName] = df[columnName].dt.strftime('%Y-%m-%d %H:%M:%S.%f')
            
        else:
            df[columnName].astype(bool)
            
        return df  
    
    
    ###
    # Description: performs the special upload on a Subject per Row that is Time Series
    # PARAMS: df (pandas DataFrame), docID (integer), column_info (tuple)
    # RETURN: (Boolean, String/None) - True if the upload was successful, string if an error occurred and it would be the specific error message
    ### 
    def specialUploadToDatabase(self, df, docID, column_info):
        
        columnHeaders = DBClient.getTableColumns(self.tableName)
        
        columnName = column_info[0][0]
        dt = column_info[0][1]
        
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
    
    
    ###
    # Description: makes sure the column names in the dataframe are lowercased and contains no whitespaces 
    # PARAMS: df (pandas DataFrame)
    # RETURN: DataFrame - the dataframe that was updated
    ###
    def __adjustDataframeColumnNames(self, df):
        df.columns = map(str.lower, df.columns)
        df.columns = df.columns.str.replace(' ', '')
        
        return df 
    
    
    ###
    # Description: performs the uploading from the CSV to the database
    # PARAMS: df (pandas DataFrame), docID (integer), column_info (List of Tuple), organizedColumns (List of String)
    # RETURN: (Boolean, String/None) - True if the upload was successful, string if an error occurred and it would be the specific error message
    ### 
    def uploadToDatabase(self, df, filename, docID, column_info, organizedColumns):
        errorMessage = None
        columnFlag = False 
        
        df = self.__adjustDataframeColumnNames(df)
        
        # if subject per column, need to transpose the dataframe 
        if self.subjectPerCol is True:
            columnFlag = True
            df = Helper.transposeDataFrame(df, True)
            df = self.__adjustDataframeColumnNames(df)
            
        filename = Helper.modifyFileName(filename)  
        
        df.columns = self.headers
        
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
            df = df[organizedColumns]   # setting the dataframe columns to the correct order based on database table organization
            df['subject_id'] = listOfSubjects
        
        
        else:
            if self.subjectOrganization == 'file':
                subjectID, errorMessage = self.subjectHandler(filename)
                df = df[organizedColumns]
                df['subject_id'] = subjectID
                
            else:
                listOfSubjects = []
                listOfSubjectNum = list(df.index) 
                
                for num in listOfSubjectNum:
                    currID, errorMessage = self.subjectHandler("", num)
                    listOfSubjects.append(currID)
                    
                df = df[organizedColumns]
                df['subject_id'] = listOfSubjects
    
        df['doc_id'] = docID
        
        try:
            with transaction.atomic():  # make transaction so if error occurred, will perform a rollback
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
    
    