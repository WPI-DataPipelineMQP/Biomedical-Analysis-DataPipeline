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


def insertToStudy(study_name):
    
    study_insert_template = ("INSERT INTO Study "
               "(study_name, total_sample_size) "
               "VALUES (%s, %s)")
    
    new_study = (study_name, 0)
    
    result = DBClient.executeCommand(study_insert_template, new_study)

        
    if not result :
        print('ERROR: Error Found When Attempting to Insert {} to Study Table'.format(study_name))
    
    return result