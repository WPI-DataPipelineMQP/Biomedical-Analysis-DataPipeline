import psycopg2
from decouple import config
import sys

# Script to clear all data from the database and then repopulate it with test data.
# While working on this project, we often used anonymous data from one of Professor Claypool’s and
# Professor Lammert’s previous IQPs called “The Effects of Exercise on Cognitive on Performance” for testing purposes.
# This script has many functions for repopulating different tables, with some of the functions currently being unused


db = None
HOST = config('DATABASE_HOST')
USER = config('DATABASE_USER')
PASSWORD = config('DATABASE_PASSWORD')
DATABASE_NAME = config('DATABASE_NAME')
PORT = config('DATABASE_PORT')

# Connect to database
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

# Clear contents of all tables. Currently does not affect dynamic data category tables so these need to be dropped manually
#myCursor.execute("SET FOREIGN_KEY_CHECKS = 0")
myCursor.execute("DROP TABLE IF EXISTS flanker_1")
myCursor.execute("DROP TABLE IF EXISTS corsi_1")
myCursor.execute("DROP TABLE IF EXISTS heartrate_1")
myCursor.execute('TRUNCATE DataCategoryStudyXref RESTART IDENTITY CASCADE')
myCursor.execute('TRUNCATE Attribute RESTART IDENTITY CASCADE')
myCursor.execute('TRUNCATE Document RESTART IDENTITY CASCADE')
myCursor.execute('TRUNCATE DataCategory RESTART IDENTITY CASCADE')
myCursor.execute('TRUNCATE Subject RESTART IDENTITY CASCADE')
myCursor.execute('TRUNCATE StudyGroup RESTART IDENTITY CASCADE')
myCursor.execute('TRUNCATE Study RESTART IDENTITY CASCADE')
#myCursor.execute("SET FOREIGN_KEY_CHECKS = 1")

# Recreate dynamic data category tables for Exercise IQP test data
myCursor.execute("CREATE TABLE heartrate_1(" +
                             "data_id SERIAL," +
                             "date_time timestamp," +
                             "heart_rate INT," +
                             "subject_id INT," +
                             "doc_id INT," +
                             "PRIMARY KEY (data_id)," +
                             'CONSTRAINT FK_HeartRate_SubjectID FOREIGN KEY(subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE' +
                             ")")


myCursor.execute("CREATE TABLE corsi_1(" +
                             "data_id SERIAL," +
                             "highest_corsi_span INT," +
                             "num_of_items INT," +
                             "binary_result INT," +
                             "sequence_number INT," +
                             "trial INT," +
                             "subject_id INT," +
                             "doc_id INT," +
                             "PRIMARY KEY (data_id)," +
                             'CONSTRAINT FK_Corsi_SubjectID FOREIGN KEY(subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE' +
                             ")")


myCursor.execute("CREATE TABLE flanker_1(" +
                             "data_id SERIAL," +
                             "flanker_code VARCHAR(255)," +
                             "is_congruent INT," +
                             "result INT," +
                             "response_time INT," +
                             "trial INT," +
                             "subject_id INT," +
                             "doc_id INT," +
                             "PRIMARY KEY (data_id)," +
                             'CONSTRAINT FK_Flanker_SubjectID FOREIGN KEY(subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE' +
                             ")")

######################################
# Input: None
# Returns: None
# Description: Populates study table with Exercise IQP
######################################
def populateStudyTable():
    try:
        myCursor = db.cursor()
        study_insert_template = ("""INSERT INTO Study """
               "(study_name, study_description, is_irb_approved, institutions_involved, visibility) "
               "VALUES (%s, %s, %s, %s, %s)")
        description = "The goal of our project is to explore relationships between exercise and cognition. " \
                      "We would like to correlate the exercise faculties of physical exertion and movement with" \
                      " the cognitive faculties of attention and memory. We performed our experiment by giving" \
                      " cognitive tests to two groups: students participating in gym classes and students resting" \
                      " while watching a show of their choice. We measured physical exertion with the activity " \
                      "trackers Fitbit Inspire HR and Axivity AX3 and measured cognitive ability using the" \
                      " Flanker and Corsi tests. Based on our experiment, with 32 participants in the control" \
                      " group and 30 in the exercise group, we found that both groups showed a significant " \
                      "improvement on the attention test while only the exercise group showed a significant " \
                      "improvement on the memory test. We were also able to distinguish the exercise group from the" \
                      " control group with significant differences in both heart rate and movement, showing that" \
                      " the exercise group exerted much more effort during their activity sessions. There was not" \
                      " a statistically significant correlation between heart rate or movement with increased" \
                      " cognitive performance."
        exercise_study = ('Exercise IQP', description, True, 'Worcester Polytechnic Institute', 'Public (Testing)')

        myCursor.execute(study_insert_template, exercise_study)
        print("Study Table populated successfully!")
        db.commit()
    except psycopg2.DatabaseError as e:
        print(e)
        print("ERROR: Issue Found When Populating Study Table")


######################################
# Input: None
# Returns: None
# Description: Populate study group table with control group and experimental group
######################################
def populateStudyGroupTable():
    try:
        myCursor = db.cursor()
        group_insert_template = ("""INSERT INTO StudyGroup """
               "(study_group_name, study_id, study_group_description) "
               "VALUES (%s, %s, %s)")

        # Add control group
        description = "This group partook in a leisure activity of watching a show on a computer for 30 minutes" \
                      " while sitting down."
        control_group = ('Control', 1, description)
        myCursor.execute(group_insert_template, control_group)
        db.commit()

        # Add experimental group
        description = "This group completed gym workouts as part of their physical education classes."
        experimental_group = ('Experimental', 1, description)
        myCursor.execute(group_insert_template, experimental_group)
        db.commit()

        print("StudyGroup Table populated successfully!")
    except psycopg2.DatabaseError as e:
        print(e)
        print("ERROR: Issue Found When Populating StudyGroup Table")

######################################
# Input: template - String of SQL statement with placeholder values
# args - tuple of arguments for the placeholders in the template
# Returns: Boolean based on whether SQL statement ran successfully
# Description: Executes insert SQL statements using a template and tuple of arguments
######################################
def executeCommand(template, args):
    try:
        myCursor = db.cursor()
        myCursor.execute(template, args)
        db.commit()
        return True
    except psycopg2.DatabaseError as e:
        print(e)
        return False

######################################
# Input: None
# Returns: None
# Description: Populate subject table with all experimental and control group subjects
######################################
def populateSubjectTable():
    try:
        for i in range(1, 34):
            addSubject(i, 2)

        for i in range(1, 38):
            addSubject("C"+str(i), 1)

        print("Subject Table populated successfully!")
    except psycopg2.DatabaseError as e:
        print(e)
        print("ERROR: Issue Found When Populating Subject Table")

######################################
# Input: subject_number - String of the Subject_number for new subject
# studyGroup_id - int of the id of the study group that the new subject belongs to
# Returns: None
# Description: Insert subject into Subject table given their subject number and the id of their study group
######################################
def addSubject(subject_number, studyGroup_id):
    subject_insert_template = ("""INSERT INTO Subject """
                               "(subject_number, study_group_id) "
                               "VALUES (%s, %s)")
    subject = (subject_number, studyGroup_id)
    executeCommand(subject_insert_template, subject)

######################################
# Input: None
# Returns: None
# Description: Populates data category table with heartrate, corsi, and flanker
######################################
def populateDataCategoryTable():
    try:
        myCursor = db.cursor()
        dataCategory_insert_template = ("""INSERT INTO DataCategory """
               "(data_category_name, is_time_series, has_subject_name, dc_table_name, dc_description, subject_organization) "
               "VALUES (%s, %s, %s, %s, %s, %s)")

        # Add heart rate data category
        description = "Time series heart rate data collected by a FitBit Inspire HR"
        heart_rate_data_category = ('HeartRate', True, False, 'heartrate_1', description, 'file')
        myCursor.execute(dataCategory_insert_template, heart_rate_data_category)
        db.commit()

        # Add Corsi data category
        description = "Test results from Corsi memory tests"
        corsi_data_category = ('Corsi', False, False, 'corsi_1', description, 'file')
        myCursor.execute(dataCategory_insert_template, corsi_data_category)
        db.commit()

        # Add Flanker data category
        description = "Test results from Flanker attention tests"
        flanker_data_category = ('Flanker', False, False, 'flanker_1', description, 'file')
        myCursor.execute(dataCategory_insert_template, flanker_data_category)
        db.commit()

        print("DataCategory Table populated successfully!")
    except psycopg2.DatabaseError as e:
        print(e)
        print("ERROR: Issue Found When Populating DataCategory Table")

######################################
# Input: None
# Returns: None
# Description: Populates datacategory_study_xref table with heartrate, corsi, and flanker for Exercise IQP
######################################
def populateDataCategoryStudyXrefTable():
    try:
        myCursor = db.cursor()
        dataCategoryStudyXref_insert_template = ("""INSERT INTO DataCategoryStudyXref """
               "(data_category_id, study_id) "
               "VALUES (%s, %s)")

        heart_rate_exercise_xref = (1, 1)
        myCursor.execute(dataCategoryStudyXref_insert_template, heart_rate_exercise_xref)
        db.commit()

        corsi_exercise_xref = (2, 1)
        myCursor.execute(dataCategoryStudyXref_insert_template, corsi_exercise_xref)
        db.commit()

        flanker_exercise_xref = (3, 1)
        myCursor.execute(dataCategoryStudyXref_insert_template, flanker_exercise_xref)
        db.commit()

        print("DataCategoryStudyXref Table populated successfully!")
    except psycopg2.DatabaseError as e:
        print(e)
        print("ERROR: Issue Found When Populating DataCategoryStudyXref Table")

######################################
# Input: None
# Returns: None
# Description: Populate heart rate table with 1 record for control subject 1 and 1 record for experimental subject 1
# Currently unused.
######################################
def populateHeartRateTable():
    try:
        myCursor = db.cursor()
        heart_rate_insert_template = ("INSERT INTO HeartRate_1 "
               "(date_time, heart_rate, subject_id) "
               #"VALUES (%s, %s, %s)")
               "VALUES (STR_TO_DATE(%s, %s), %s, %s)")

        datetime_format = "%Y-%m-%d  %H:%i:%s %p"

        # Add control subject record
        control_subject_record = ("2019-11-13  14:15:01", datetime_format, 75, 1) # Insert using datetime
        # control_subject_record = ("11/13/2019  2:15:01 PM", 75, 1) # Insert using string
        myCursor.execute(heart_rate_insert_template, control_subject_record)
        db.commit()

        # Add experimental subject
        experimental_subject_record = ("2019-11-13  11:00:00", datetime_format, 85, 1)
        # experimental_subject_record = ("11/5/2019  11:00:00 AM", 85, 1)
        myCursor.execute(heart_rate_insert_template, experimental_subject_record)
        db.commit()

        print("HeartRate Table populated successfully!")
    except psycopg2.DatabaseError as e:
        print(e)
        print("ERROR: Issue Found When Populating HeartRate Table")

######################################
# Input: None
# Returns: None
# Description: Populate attribute table with info for every column in the HeartRate, Corsi, and Flanker tables
######################################
def populateAttributeTable():
    try:
        myCursor = db.cursor()
        attribute_insert_template = ("""INSERT INTO Attribute """
                   "(attr_name, data_type, data_category_id) "
                   "VALUES (%s, %s, %s)")

        heartrate_datetime = ("date_time", "DATETIME", 1)
        executeCommand(attribute_insert_template, heartrate_datetime)

        heartrate_heartrate = ("heart_rate", "INT", 1)
        executeCommand(attribute_insert_template, heartrate_heartrate)

        corsi_highestCorsiSpan = ("highest_corsi_span", "INT", 2)
        executeCommand(attribute_insert_template, corsi_highestCorsiSpan)

        corsi_numOfItems = ("num_of_items", "INT", 2)
        executeCommand(attribute_insert_template, corsi_numOfItems)

        corsi_binaryResult = ("binary_result", "INT", 2)
        executeCommand(attribute_insert_template, corsi_binaryResult)

        corsi_sequenceNumber = ("sequence_number", "INT", 2)
        executeCommand(attribute_insert_template, corsi_sequenceNumber)

        corsi_trial = ("trial", "INT", 2)
        executeCommand(attribute_insert_template, corsi_trial)

        flanker_flankerCode = ("flanker_code", "VARCHAR(255)", 3)
        executeCommand(attribute_insert_template, flanker_flankerCode)

        flanker_isCongruent = ("is_congruent", "INT", 3)
        executeCommand(attribute_insert_template, flanker_isCongruent)

        flanker_result = ("result", "INT", 3)
        executeCommand(attribute_insert_template, flanker_result)

        flanker_responseTime = ("response_time", "INT", 3)
        executeCommand(attribute_insert_template, flanker_responseTime)

        flanker_trial = ("trial", "INT", 3)
        executeCommand(attribute_insert_template, flanker_trial)

        print("Attribute Table populated successfully!")
    except psycopg2.DatabaseError as e:
        print(e)
        print("ERROR: Issue Found When Populating Attribute Table")


# Functions that are actually called when running this script
populateStudyTable()
populateStudyGroupTable()
populateDataCategoryTable()
populateDataCategoryStudyXrefTable()
populateAttributeTable()

db.close()
