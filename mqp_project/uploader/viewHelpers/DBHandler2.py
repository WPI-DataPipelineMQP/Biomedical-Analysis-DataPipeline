from datapipeline.database import DBClient
from datapipeline.models import Study, StudyGroup, DataCategory, DataCategoryStudyXref, Attribute

def insertToStudyGroup(groupName, description, studyID):
    studyObj = Study.objects.get(study_id=studyID)
    newStudyGroup = StudyGroup.objects.create(study_group_name=groupName,
                                              study_group_description=description,
                                              study=studyObj)
    
    
def getGroupID(groupName, studyID):
    return (StudyGroup.objects.get(study_group_name=groupName, study=studyID)).study_group_id 



def insertToDataCategory(category_name, time_series_val, hasSubjectNames, dc_table_name, description):
    
    try:
        newDataCategory = DataCategory.objects.create(data_category_name=category_name,
                                                      is_time_series=time_series_val,
                                                      has_subject_name=hasSubjectNames,
                                                      dc_table_name=dc_table_name,
                                                      dc_description=description)
        
        return True
    
    except:
        return False 



def getDataCategoryID(tableName, is_time_series):
    
    return (DataCategory.objects.get(dc_table_name=tableName, is_time_series=is_time_series)).data_category_id  

    
    
    
def insertToDataCategoryXref(category_id, study_id):
    
    try:
        studyObj = Study.objects.get(study_id=study_id)
        dcObj = DataCategory.objects.get(data_category_id=category_id)
        newXref = DataCategoryStudyXref.objects.create(data_category=dcObj,
                                                       study=studyObj)
        
        return True 
    
    except:
        return False 
    
    
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
            
        except:
            return False 
        
    
    return True


def createNewTable(myMap):
    result = False 
    
    if myMap.get('createTable') is False:
        dataTypeMap = {
            '1' : 'TEXT',
            '2' : 'INT',
            '3' : 'FLOAT(10,5)',
            '4' : 'Datetime',
            '5' : 'BOOLEAN'
        }

        table_name = myMap.get('tableName')
        
        dataID_field = "data_id INT AUTO_INCREMENT,"
        subjectID_field = "subject_id INT,"
        pk_field = "PRIMARY KEY (data_id),"
        fk_field = "CONSTRAINT FK_{}_SubjectID FOREIGN KEY(subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE)".format(table_name.upper())
    
        stmt = "CREATE TABLE {}({}".format(table_name, dataID_field)
    
        for column in myMap.get('columns'):
            field_name = column[0]
            data_type = dataTypeMap.get(column[1]) 
        
            tmp_stmt = "{} {},".format(field_name, data_type)
        
            stmt += tmp_stmt
        
        stmt += subjectID_field
        stmt += pk_field
        stmt += fk_field
        
        result = DBClient.createTable(stmt, table_name, 1)
        

    return result