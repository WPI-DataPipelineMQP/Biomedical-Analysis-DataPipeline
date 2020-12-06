from django.db import IntegrityError, transaction
from datapipeline.models import Study, StudyGroup, DataCategory, DataCategoryStudyXref
from . import Helper, DBHandler2 

def updateFieldsFromDataCategory(data_category_id, fields):
    where_params = [('data_category_id', data_category_id, False)]
    
    tableName = (DataCategory.objects.get(data_category_id=data_category_id)).dc_table_name
    isTimeSeries = (DataCategory.objects.get(data_category_id=data_category_id)).is_time_series
    hasSubjectNames = (DataCategory.objects.get(data_category_id=data_category_id)).has_subject_name
                
    fields['tableName'] = tableName
    fields['isTimeSeries'] = isTimeSeries
    fields['hasSubjectNames'] = hasSubjectNames
    
    return fields


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
    
    insertSuccess = DBHandler2.insertToDataCategory(data_category_name, time_series_int, has_subjectNames_int, dc_table_name, description)
    
    if insertSuccess is False:
        return myMap, False
    
    data_category_id = DBHandler2.getDataCategoryID(dc_table_name, time_series_int)
    
    myMap['DC_ID'] = data_category_id
        
    insertSuccess = DBHandler2.insertToDataCategoryXref(data_category_id, study_id)

    if insertSuccess is False:
        return myMap, False
    
    
    data_category_name = data_category_name.replace(" ", "_")
    myMap['tableName'] = data_category_name + '_' + str(study_id)

    return myMap, True



def handleMissingDataCategoryID(studyID, subjectRule, isTimeSeries, uploaderInfo, otherInfo):
    errorMessage = ''
    hasSubjectNames = False 
    
    myFields, myExtras = otherInfo[0], otherInfo[1]
            
    subjectVal = myFields.get('hasSubjectID')
            
    if subjectVal == 'y':
        hasSubjectNames = True 
            
         
    uploaderInfo['hasSubjectNames'] = hasSubjectNames 
    uploaderInfo['isTimeSeries'] = isTimeSeries
                       
    myMap = {
        'categoryName': uploaderInfo.get('categoryName'),
        'isTimeSeries': isTimeSeries,
        'hasSubjectNames': hasSubjectNames,
        'DC_description': myFields.get('dataCategoryDescription')
    }
    
    cleanResult = Helper.getCleanFormat(myExtras)
    
    try:
        with transaction.atomic():
            myMap, noErrors = dataCategoryHandler(myMap, studyID) 
                
            if noErrors is False:
                errorMessage = "Error found when updating the DataCategory Table!"
                raise IntegrityError()
            
            uploaderInfo['tableName'] = myMap.get('tableName')
            uploaderInfo['dcID'] = myMap.get('DC_ID')
            
            myMap['columns'] = cleanResult

            cleanAttributeFormat = Helper.seperateByName(myExtras, 4, False)
            
            noErrors = DBHandler2.insertToAttribute(cleanAttributeFormat, myMap.get('DC_ID'))

            if noErrors is False:
                errorMessage = "Error found when inserting to Attribute table!"
                raise IntegrityError()
            
            noErrors = DBHandler2.createNewTable(myMap)
            
            if noErrors is False:
                errorMessage = "Error found when creating the new table!"
                raise IntegrityError()
                
    except IntegrityError:
        print('SHOULD ROLLBACK')

        return uploaderInfo, errorMessage
    
    
    return uploaderInfo, None