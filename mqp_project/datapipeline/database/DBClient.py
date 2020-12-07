import mysql.connector
from django.db import connection
from django.conf import settings
import pandas as pd 
import numpy as np
import sqlalchemy as sql

def dictfetchall(cursor):
    # "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    rows =  [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

    # if list is empty
    if not rows:
        rows = [
            dict.fromkeys(columns, "")
        ]

    return rows

def getTables():
    try:
        myTables = []
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            
            tables_raw = cursor.fetchall()
            
            if not tables_raw:
                return []
            
            for table in tables_raw:
                myTables.append(table[0])
                
            return myTables
        
    except:
        print("ERROR GETTING TABLES")
        return []


def getTableColumns(table_name):
    myColumns = []
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM {}".format(table_name))
        
            columns_raw = cursor.fetchall()
        
            for column in columns_raw:
                myColumns.append(column[0])
        
    except:
        print('Error')
        
    return myColumns


def performFetchAll(stmt):
    result = []
    foundError = False 
    try:
        with connection.cursor() as cursor:
            cursor.execute(stmt)
            
            result = cursor.fetchall() 
            
    except:
        foundError = True 
        
    
    return result, foundError
        
            
            


def createTable(stmt, table_name, verbose=0):

    try:
        with connection.cursor() as cursor:
            if verbose == 1:
                print(stmt)
                
            cursor.execute(stmt)
            
            print('\nCreated {} Table Successfully'.format(table_name))
            
    
    except:
        print("\nIssue Found When Creating {} Table".format(table_name))
        return False 
        
    return True
        




def buildQuery(args):
    stmt = "SELECT " + args['selectors'] + " "
    stmt += "FROM " + args['from'] + " "


    if args['join-type'] != None and args['join-stmt'] != None:
        stmt += args['join-type'] + " " + args['join-stmt'] + " "

    if args['where'] != None :
        stmt += "WHERE " + args['where'] + " "

    if args['group-by'] != None :
        stmt += "GROUP BY " + args['group-by'] + " "

    if args['order-by'] != None :
        stmt += "ORDER BY " + args['order-by'] + " "


    return stmt


def executeQuery(args, verbose=0):
    try:
        with connection.cursor() as cursor:
            stmt = buildQuery(args)
            
            if verbose == 1:
                print(stmt)
            
            stmt = buildQuery(args)
        
            # if verbose == 1:
            #     print(stmt)
            
            cursor.execute(stmt)
            
            result = cursor.fetchall()
            
            if not result:
                return []
            
            return result

    # except:
    #     print('ERROR IN SELECT')
    #     return []
    except mysql.connector.Error as e:
        print(e)
        return []
        
# Execute an insert, update, or delete command
# @param template - String of sql command with string formatters (%s)
# @param args - tuple of arguments corresponding to the string placeholders in the template
def executeCommand(template, args):
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(template, args)
            
        return True
        
    except:
        print('ERROR IN EXECUTE COMMAND')
            
        return False
    
def tryExecuteCommand(template, args):
    with connection.cursor() as cursor:
        cursor.execute(template, args)
        
    
def dfInsert(df, tableName):
    db_engine = sql.create_engine(settings.DB_CONNECTION_URL)
    df.to_sql(name=tableName, con=db_engine, if_exists='append', index=False, chunksize=20000)
