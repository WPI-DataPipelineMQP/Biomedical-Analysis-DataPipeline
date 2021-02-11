import mysql.connector
import psycopg2
from django.db import connection
from django.conf import settings
import pandas as pd 
import numpy as np
import sqlalchemy as sql


def getTables():
    try:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT table_name FROM information_schema.tables
						 WHERE table_schema = 'public'""")
            
            myTables = [res[0] for res in cursor.fetchall()]
            
            return myTables
        
    except:
        print("ERROR GETTING TABLES")
    
    return []


def getTableColumns(table_name):
    
    try:
        with connection.cursor() as cursor:
            stmt = "select * from {} LIMIT 0".format(table_name)
            print(stmt)
            cursor.execute("select * from {} LIMIT 0".format(table_name))
            colNames = [res[0] for res in cursor.description]
            
            print(colNames)
            return colNames
            
        
    except:
        print('Error')
        
    return []


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
            
            cursor.close()
        
        connection.commit()
            
    
    except Exception as e:
        return False, str(e)
        
    return True, None 
        




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

    print("STATEMENT: " + stmt)
    return stmt


def executeQuery(args, verbose=0):
    try:
        with connection.cursor() as cursor:
            stmt = buildQuery(args)
            
            if verbose == 1:
                print(stmt)
            
            stmt = buildQuery(args)
            
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
            
        connection.commit()
            
        return True
        
    except:
        print('ERROR IN EXECUTE COMMAND')
            
        return False

 
def executeStmt(stmt):
    with connection.cursor() as cursor:
        cursor.execute(stmt)
        
    connection.commit()
        
    
def dfInsert(df, tableName):
    db_engine = sql.create_engine(settings.DB_CONNECTION_URL)
    df.to_sql(name=tableName, con=db_engine, if_exists='append', index=False, chunksize=20000)
    

def deleteData(tableName, docID):
    with connection.cursor() as cursor:
        stmt = f'DELETE FROM {tableName} WHERE doc_id = {docID}'
        
        cursor.execute(stmt)
        
    connection.commit()
