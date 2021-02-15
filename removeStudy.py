import psycopg2
from decouple import config
import sys

db = None
HOST = config('DATABASE_HOST')
USER = config('DATABASE_USER')
PASSWORD = config('DATABASE_PASSWORD')
DATABASE_NAME = config('DATABASE_NAME')
PORT = config('DATABASE_PORT')

db = psycopg2.connect(
    host = HOST,
    user = USER,
    password = PASSWORD,
    database = DATABASE_NAME,
    port = PORT
)

if db :
    print('Connected to PostgreSQL Successfully!')

else :
	raise Exception('Connection to PostgreSQL Failed')
	exit(1)

myCursor = db.cursor()


table_name = input('Enter Data Category Table Name: ')
dcID = f"SELECT data_category_id FROM DataCategory WHERE dc_table_name = '{table_name}'"

myCursor.execute(dcID)

dcID = myCursor.fetchall()

if len(dcID) == 0:
	sys.exit(1)

dcID = dcID[0][0]
print(dcID)

dcXrefID = f"SELECT dc_study_id FROM DataCategoryStudyXref WHERE data_category_id = {dcID}"

dcXrefID = myCursor.fetchall()

if len(dcXrefID) == 0:
	print('here')
	sys.exit(1)

dcXrefID = dcXrefID[0][0]

dcAttributes = f"SELECT attr_id FROM Attribute WHERE data_category_id = {dcID}"

myCursor.execute(dcAttributes)

dcAttributes = myCursor.fetchall()
myAttributeID = []

if len(dcAttributes) != 0:
	for tup in dcAttributes:
		myAttributeID.append(tup[0])

allSubjectIDs = f"SELECT subject_id FROM {table_name}"


myCursor.execute(allSubjectIDs)

allSubjectIDs = myCursor.fetchall()

mySubjectIDs = []

if len(allSubjectIDs) != 0:
	for tup in allSubjectIDs:
		mySubjectIDs.append(tup[0])

print(dcID)
print(dcXrefID)
print(myAttributeID)
print(mySubjectIDs)

