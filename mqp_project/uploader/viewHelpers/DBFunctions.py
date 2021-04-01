from datapipeline.database import DBClient
from datapipeline.models import Study, StudyGroup, Subject, DataCategory, DataCategoryStudyXref, Attribute

###
# Description: does an insert to the StudyGroup table
# PARAMS: groupName (String), description (String), studyID (Integer)
# RETURN: None
###
def insertToStudyGroup(groupName, description, studyID):
    studyObj = Study.objects.get(study_id=studyID)
    newStudyGroup = StudyGroup.objects.create(study_group_name=groupName,
                                              study_group_description=description,
                                              study=studyObj)
    
###
# Description: gets the StudyGroup ID (if exists)
# PARAMS: groupName (String), studyID (Integer)
# RETURN: Integer - will return a -1 if ID does not exist
###    
def getGroupID(groupName, studyID):
    
    groupExists = StudyGroup.objects.filter(study_group_name=groupName, study=studyID).exists()
    
    if groupExists:
        return (StudyGroup.objects.get(study_group_name=groupName, study=studyID)).study_group_id 
    
    return -1


###
# Description: gets the DataCategory ID (if exists)
# PARAMS: category_name (String), timeSeries (Boolean), subjectOrg (String), studyID (Integer)
# RETURN: Integer - will return a -1 if ID does not exist
###
def getDataCategoryIDIfExists(category_name, timeSeries, subjectOrg, studyID):
    data_category_id = -1
    
    categoryExists = DataCategory.objects.filter(data_category_name=category_name, is_time_series=timeSeries, subject_organization=subjectOrg).exists()
        
    if categoryExists:
        potentialInstances = DataCategory.objects.filter(data_category_name=category_name, is_time_series=timeSeries, subject_organization=subjectOrg)
            
        for dc in potentialInstances:
            xrefExists = DataCategoryStudyXref.objects.filter(data_category=dc, study=studyID).exists()
                
            if xrefExists:
                data_category_id = (DataCategoryStudyXref.objects.get(data_category=dc, study=studyID)).data_category.data_category_id
                break
            
    return data_category_id


###
# Description: does an insert into the DataCategory database table
# PARAMS: category_name (String), time_series_val (Boolean), hasSubjectNames (Boolean), dc_table_name (String), description (String), subjectOrg (String)
# RETURN: Tuple - (Boolean, String)
###
def insertToDataCategory(category_name, time_series_val, hasSubjectNames, dc_table_name, description, subjectOrg):
    
    try:
        newDataCategory = DataCategory.objects.create(data_category_name=category_name,
                                                      is_time_series=time_series_val,
                                                      has_subject_name=hasSubjectNames,
                                                      dc_table_name=dc_table_name,
                                                      dc_description=description,
                                                      subject_organization=subjectOrg)
        
        return True, ''
    
    except Exception as e:
        
        return False, str(e)


###
# Description: gets the DataCategory ID
# PARAMS: tableName (String), is_time_series (Boolean)
# RETURN: Integer - the DataCategory ID
###
def getDataCategoryID(tableName, is_time_series):
    
    return (DataCategory.objects.get(dc_table_name=tableName, is_time_series=is_time_series)).data_category_id  

    
    
###
# Description: does an insert into the DataCategoryStudyXref database table
# PARAMS: category_id (Integer), study_id (Integer)
# RETURN: Tuple - (Boolean, String)
###
def insertToDataCategoryXref(category_id, study_id):
    
    try:
        studyObj = Study.objects.get(study_id=study_id)
        dcObj = DataCategory.objects.get(data_category_id=category_id)
        newXref = DataCategoryStudyXref.objects.create(data_category=dcObj,
                                                       study=studyObj)
        
        return True, '' 
    
    except Exception as e:
        return False, str(e)
    
###
# Description: does an insert into the Attribute database table
# PARAMS: attributes (Dictionary), dcID (Integer)
# RETURN: Tuple - (Boolean, String)
###   
def insertToAttribute(attributes, dcID):
    
    for colName in attributes:
        currDict = attributes.get(colName)
        name = colName
        description = currDict.get('description')
        dataType = currDict.get('dataType')
        unit = currDict.get('unit')
        device = currDict.get('deviceUsed')
        
        try:
            dcObj = DataCategory.objects.get(data_category_id=dcID)
            newAttribute = Attribute.objects.create(attr_name=name,
                                                    attr_description=description,
                                                    data_type=dataType,
                                                    unit=unit,
                                                    device_name=device,
                                                    data_category=dcObj) 
            
        except Exception as e:
            return False, str(e) 
        
    
    return True, ''

###
# Description: drops the specified table from the database
# PARAMS: tableName (String)
# RETURN: None
###
def dropTable(tableName):
    stmt = f"DROP TABLE IF EXISTS {tableName}"
    
    DBClient.executeStmt(stmt)
    
    print(f"DROPPED TABLE: {tableName}")
    
###
# Description: creates a new database table 
# PARAMS: myMap (Dictionary)
# RETURN: Tuple - (Boolean, String)
###
def createNewTable(myMap):
    result = False 
    
    if myMap.get('createTable') is False:
        dataTypeMap = {
            '1' : 'TEXT',
            '2' : 'INT',
            '3' : 'NUMERIC(10,5)',
            '4' : 'timestamp',
            '5' : 'BOOLEAN'
        }

        table_name = myMap.get('tableName')
        #table_name = table_name.lower()
        
        # setting the known statements within the create table query statement
        dataID_field = "data_id SERIAL,"
        subjectID_field = "subject_id INT,"
        docID_field = "doc_id INT,"
        pk_field = "PRIMARY KEY (data_id),"
        fk_field = "CONSTRAINT FK_{}_SubjectID FOREIGN KEY(subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE)".format(table_name.upper())
        
        
        # the following lines builds the actual query statement
        stmt = "CREATE TABLE {}({}".format(table_name, dataID_field)
        
        for column in myMap.get('columns'):
            field_name = column[0]
            data_type = dataTypeMap.get(column[1]) 
        
            tmp_stmt = "{} {},".format(field_name, data_type)
        
            stmt += tmp_stmt
        
        stmt += subjectID_field
        stmt += docID_field
        stmt += pk_field
        stmt += fk_field
        
        result, errorMessage = DBClient.createTable(stmt, table_name, 1)
        

    return result, errorMessage
        

###
# Description: gets the attribute of the specified table
# PARAMS: tableName (String)
# RETURN: Tuple - (String, String)
###
def getAttributeOfTable(tableName):
    
    dc_ID = (DataCategory.objects.get(dc_table_name=tableName)).data_category_id
    
    dc_obj = DataCategory.objects.get(data_category_id=dc_ID)
    
    attributeObj = Attribute.objects.get(data_category=dc_obj)
    
    attributeName = attributeObj.attr_name 
    attributeType = attributeObj.data_type
    
    return attributeName, attributeType


###
# Description: gets the schema of the specified tablename with the corresponding data category ID
# PARAMS: tableName (String), dcID (Integer)
# RETURN: String - a string of the table schema
###
def getTableSchema(tableName, dcID):
    string = '{} SCHEMA: '.format(tableName)
    
    columns = DBClient.getTableColumns(tableName)
    columns = columns[1:-2]
    
    for i in range(0, len(columns), 1):
        position = ''
        if i != ( len(columns)-1 ):
            position = "{} [ position = {} ], ".format(columns[i], i)
            
            
        else:
            position = "{} [ position = {} ]".format(columns[i], i)
            
        string += position
        
    return string


###
# Description: gets all the data categories of the study with the provided study ID
# PARAMS: studyID (Integer)
# RETURN: List of String - list of all the data category names of the particular study
###
def getAllDataCategoriesOfStudy(studyID):
    
    studyObj = Study.objects.get(study_id=studyID)
    
    studysDCXrefs = DataCategoryStudyXref.objects.filter(study=studyObj)
    
    studysDCs = []
    
    for dcXref in studysDCXrefs:
        dc_obj = dcXref.data_category
        
        name = dc_obj.data_category_name
        
        studysDCs.append(name)
        
    return studysDCs 


###
# Description: gets the Subject ID from the Subject database table
# PARAMS: subjectNumber (String), study_group_id (Integer)
# RETURN: Integer - returns a -1 if the subject does not exist within the table
###
def getSubjectID(subjectNumber, study_group_id):
    subjectID = -1 
    
    groupObj = StudyGroup.objects.get(study_group_id=study_group_id)
    subjectExist = Subject.objects.filter(subject_number=subjectNumber, study_group=groupObj).exists()
    
    if subjectExist:
        subjectID = (Subject.objects.get(subject_number=subjectNumber, study_group=groupObj)).subject_id
        
    return subjectID


###
# Description: does an insert into the Subject database table 
# PARAMS: subjectNumber (String), study_group_id (Integer)
# RETURN: Boolean - True if the insert into the Subject database table was successful
def insertToSubject(subjectNumber, study_group_id):
    
    try:
        groupObj = StudyGroup.objects.get(study_group_id=study_group_id)
        newSubject = Subject.objects.create(subject_number=subjectNumber, study_group=groupObj)
        
        return True 
    
    except:
        return False