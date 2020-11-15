from . import DBClient
import pandas as pd 
import numpy as np

def getSelectorFromTable(selector, table_name, where_params, join_info):
    where_stmt = ""
    
    for i in range(0, len(where_params)) :
        if where_params[i][2]:
            where_stmt += "{}='{}'".format(where_params[i][0], where_params[i][1])
            
        else :
            where_stmt += "{}={}".format(where_params[i][0], where_params[i][1])
        
        
        if i != (len(where_params) - 1) :
            where_stmt += " AND "
             
                
    args = {
        'selectors': selector,
        'from': table_name,
        'join-type': join_info[0],
        'join-stmt': join_info[1],
        'where': where_stmt,
        'group-by': None,
        'order-by': None
    }
    
    result = DBClient.executeQuery(args)
    
    #print('Result:', result)
    if result:
        return result[0][0]
    
    return -1

def getInfoOnStudy(selector, table_name, where_params, join_info):
    where_stmt = ""
    
    for i in range(0, len(where_params)) :
        if where_params[i][2]:
            where_stmt += "{}='{}'".format(where_params[i][0], where_params[i][1])
            
        else :
            where_stmt += "{}={}".format(where_params[i][0], where_params[i][1])
        
        
        if i != (len(where_params) - 1) :
            where_stmt += " AND "
             
                
    args = {
        'selectors': selector,
        'from': table_name,
        'join-type': join_info[0],
        'join-stmt': join_info[1],
        'where': where_stmt,
        'group-by': None,
        'order-by': None
    }
    
    result = DBClient.executeQuery(args)
    
    if result:
        result = convertToList(result)
        
        return result
    
    #print('Result:', result)
    if result:
        return result[0][0]
    
    return []

def convertToList(data):
    result = []
    
    for i in range(0, len(data), 1):
        name = data[i][0]
        result.append(name)
        
    return result


def insertToStudy(values):
    
    study_insert_template = ("INSERT INTO Study "
               "(study_name, study_description, is_irb_approved, institutions_involved, study_start_date, study_end_date, study_contact, study_notes) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    
    new_study = ()
    
    for val in values:
        new_study += (val,)
        
    print(new_study)
    
    result = DBClient.executeCommand(study_insert_template, new_study)
 
    if not result :
        print('ERROR: Error Found When Attempting to Insert {} to Study Table'.format(values[0]))
    
    return result


def insertToStudyGroup(study_group_name, description, study_id):
    
    group_insert_template = ("INSERT INTO StudyGroup "
               "(study_group_name, study_group_description, study_id) "
               "VALUES (%s, %s, %s)")
    
   
    new_group_name = (study_group_name, description, study_id)
        
    result = DBClient.executeCommand(group_insert_template, new_group_name)
        
    if not result :
        print('ERROR: Error Found When Attempting to Insert {} to StudyGroup Table'.format(study_group_name))
    
    return result


def insertToDataCategory(category_name, time_series_val, hasSubjectNames, dc_table_name, description):
    
    dataCategory_insert_template = ("INSERT INTO DataCategory "
                                    "(data_category_name, is_time_series, has_subject_name, dc_table_name, dc_description) "
                                    "VALUE (%s, %s, %s, %s, %s)")
     
    new_data_category = (category_name, time_series_val, hasSubjectNames, dc_table_name, description)
     
    result = DBClient.executeCommand(dataCategory_insert_template, new_data_category)
    
    if not result :
        print('ERROR: Error Found When Attempting to Insert Data Category Name: {} to DataCategory Table'.format(category_name))
    
    return result 


def insertToDataCategoryXref(category_id, study_id):

    dataCategoryStudyXref_insert_template = ("INSERT INTO DataCategoryStudyXref "
                                             "(data_category_id, study_id) "
                                             "VALUES (%s, %s)")

    new_data_category_xref = (category_id, study_id)
    
    result = DBClient.executeCommand(dataCategoryStudyXref_insert_template, new_data_category_xref)
    
    if not result :
        print("ERROR: Error Found When Attempting to Insert Data Category ID: {} and Study ID: {} to DataCategoryXref Table".format(category_id, study_id))
    
    return result

def insertToAttribute(attributes, dcID):
    for colName in attributes:
        currDict = attributes.get(colName)
        name = colName
        description = currDict.get('description')
        dataType = currDict.get('dataType')
        unit = currDict.get('unit')
        device = currDict.get('deviceUsed')
        
        attribute_insert_template = ("INSERT INTO Attribute "
                                        "(attr_name, attr_description, data_type, unit, device_name, data_category_id) "
                                             "VALUES (%s, %s, %s, %s, %s, %s)")

        new_attribute = (name, description, dataType, unit, device, dcID) 
        
        result = DBClient.executeCommand(attribute_insert_template, new_attribute)
        
        if not result:
            print('\nERROR during insert to Attribute\n')
            
    
        
        
def dataCategoryHandler(myMap, study_id):
    
    data_category_name = myMap.get('categoryName')
    
    time_series_int = 0 
    has_subjectNames_int = 0
    
    if myMap.get('isTimeSeries'):
        time_series_int = 1
        
    if myMap.get('hasSubjectNames'):
        has_subjectNames_int = 1
        
    myMap['createTable'] = False
    
    description = myMap.get('DC_description')
    dc_table_name = data_category_name + '_' + str(study_id)
    
    insertToDataCategory(data_category_name, time_series_int, has_subjectNames_int, dc_table_name, description)
        
    where_params = [('dc_table_name', dc_table_name, True), ('is_time_series', time_series_int, False)]

    data_category_id = getSelectorFromTable('data_category_id', 'DataCategory', where_params, [None, None])
    
    myMap['DC_ID'] = data_category_id
        
    insertToDataCategoryXref(data_category_id, study_id)
        
    myMap['tableName'] = data_category_name + '_' + str(study_id)

    return myMap


def newTableHandler(myMap):
    
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
    
        DBClient.createTable(stmt, table_name, 1)