from django.db import connection
import pandas as pd 
import numpy as np

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


def createTable(stmt, table_name, verbose=0):
    result = -1
    try:
        with connection.cursor() as cursor:
            if verbose == 1:
                print(stmt)
                
            cursor.execute(stmt)
            
            print('\nCreated {} Table Successfully'.format(table_name))
            
            result = 1
            
    
    except:
        print("\nIssue Found When Creating {} Table".format(table_name))
        
            
    return result



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
        
            if verbose == 1:
                print(stmt)
            
            cursor.execute(stmt)
            
            result = cursor.fetchall()
            
            if not result:
                return []
            
            return result
    
    except:
        print('ERROR IN SELECT')
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
