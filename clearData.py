import mysql.connector
import sys

db = None
HOST = 'localhost'
USER = 'WPI'
PASSWORD = 'DataPipeline'
DATABASE_NAME = 'DataPipeline'

tmpDB = mysql.connector.connect(
	host = HOST,
    user = USER,
    password = PASSWORD
)
     
try :
    tmpCursor = tmpDB.cursor()
    tmpCursor.execute("DROP DATABASE IF EXISTS exercise")
    tmpCursor.execute("CREATE DATABASE IF NOT EXISTS " + DATABASE_NAME)
    print('Created Database (if it didn\'t already exist):', DATABASE_NAME)
    tmpDB.close()

except mysql.connector.Error as err:
    print("Failed creating database: {}".format(err))
    exit(1)

db = mysql.connector.connect(
    host = HOST,
    user = USER,
    password = PASSWORD,
    database = DATABASE_NAME
)

if db :
    print('Connected to MySQL Successfully!')

else :
	raise Exception('Connection to MySQL Failed')
	exit(1)

myCursor = db.cursor()

myCursor.execute("SET FOREIGN_KEY_CHECKS = 0")
myCursor.execute("DROP TABLE IF EXISTS Flanker_1")
myCursor.execute("DROP TABLE IF EXISTS Corsi_1")
myCursor.execute("DROP TABLE IF EXISTS HeartRate_1")
myCursor.execute("TRUNCATE DataCategoryStudyXref")
myCursor.execute("TRUNCATE Attribute")
myCursor.execute("TRUNCATE Document")
myCursor.execute("TRUNCATE DataCategory")
myCursor.execute("TRUNCATE Demographics")
myCursor.execute("TRUNCATE Subject")
myCursor.execute("TRUNCATE StudyGroup")
myCursor.execute("TRUNCATE Study")
myCursor.execute("SET FOREIGN_KEY_CHECKS = 1")

myCursor.execute("CREATE TABLE HeartRate_1(" +
                             "data_id INT AUTO_INCREMENT," +
                             "date_time Datetime," +
                             "heart_rate INT," +
                             "subject_id INT," +
                             "doc_id INT," +
                             "PRIMARY KEY (data_id)," +
                             "CONSTRAINT FK_HeartRate_SubjectID FOREIGN KEY(subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE" +
                             ")")


myCursor.execute("CREATE TABLE Corsi_1(" +
                             "data_id INT AUTO_INCREMENT," +
                             "highest_corsi_span INT," +
                             "num_of_items INT," +
                             "binary_result INT," +
                             "sequence_number INT," +
                             "trial INT," +
                             "subject_id INT," +
                             "doc_id INT," +
                             "PRIMARY KEY (data_id)," +
                             "CONSTRAINT FK_Corsi_SubjectID FOREIGN KEY(subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE" +
                             ")")


myCursor.execute("CREATE TABLE Flanker_1(" +
                             "data_id INT AUTO_INCREMENT," +
                             "flanker_code VARCHAR(255)," +
                             "is_congruent INT," +
                             "result INT," +
                             "response_time INT," +
                             "trial INT," +
                             "subject_id INT," +
                             "doc_id INT," +
                             "PRIMARY KEY (data_id)," +
                             "CONSTRAINT FK_Flanker_SubjectID FOREIGN KEY(subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE" +
                             ")")

# Populate study table with Exercise IQP
def populateStudyTable():
    try:
        myCursor = db.cursor()
        study_insert_template = ("INSERT INTO Study "
               "(study_name, study_description, is_irb_approved, institutions_involved) "
               "VALUES (%s, %s, %s, %s)")
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
        exercise_study = ('Exercise IQP', description, 1, 'Worcester Polytechnic Institute')

        myCursor.execute(study_insert_template, exercise_study)
        print("Study Table populated successfully!")
        db.commit()
    except mysql.connector.Error as e:
        print(e)
        print("ERROR: Issue Found When Populating Study Table")

# Populate study group table with control group and experimental group
def populateStudyGroupTable():
    try:
        myCursor = db.cursor()
        group_insert_template = ("INSERT INTO StudyGroup "
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
    except mysql.connector.Error as e:
        print(e)
        print("ERROR: Issue Found When Populating StudyGroup Table")


def executeCommand(template, args):
    try:
        myCursor = db.cursor()
        myCursor.execute(template, args)
        db.commit()
        return True
    except mysql.connector.Error as e:
        print(e)
        return False


# Populate subject table with all experimental and control group subjects
def populateSubjectTable():
    try:
        for i in range(1, 34):
            addSubject(i, 2)

        for i in range(1, 38):
            addSubject("C"+str(i), 1)

        print("Subject Table populated successfully!")
    except mysql.connector.Error as e:
        print(e)
        print("ERROR: Issue Found When Populating Subject Table")

# Add individual subject
def addSubject(subject_number, studyGroup_id):
    subject_insert_template = ("INSERT INTO Subject "
                               "(subject_number, study_group_id) "
                               "VALUES (%s, %s)")
    subject = (subject_number, studyGroup_id)
    executeCommand(subject_insert_template, subject)

# Populate demographics table with randomly generated data for each subject
def populateDemographicsTable():
    try:
        for i in range(1, 71):
            addDemographic(i)

        print("Demographic Table populated successfully!")
    except mysql.connector.Error as e:
        print(e)
        print("ERROR: Issue Found When Populating Demographic Table")

# Generate random demographic data for individual subject
def addDemographic(subject_id):
    demographic_insert_template = ("INSERT INTO Demographics "
                               "(subject_id, age, sex, race, ethnicity, school_year, phone_num, address, "
                                   "height, weight, med_history) "
                               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    age = random.randint(17,25)
    sex = random.choice(["Male", "Female"])
    race = random.choice(["White", "Black", "Native American/Alaskan", "Native Hawaiian/Pacific Islander", "Asian",
                          "Other", "Unknown"])
    ethnicity = random.choice(["Latino origin", "Non-Latino origin", "Unknown"])
    school_year = random.choice([1, 2, 3, 4])
    phone_num = "".join([str(random.randint(0,9)) for i in range(10)])
    address = random.choice(["100 Institute Rd, Worcester, MA 01609", "123 Not WPI Road, Worcester, MA 01609"])
    height = random.randint(122, 214)
    weight = random.randint(40, 115)
    med_history = random.choice(["", "Cardiovascular issues", "Respiratory issues"])

    demographic = (subject_id, age, sex, race, ethnicity, school_year, phone_num, address, height, weight, med_history)
    executeCommand(demographic_insert_template, demographic)

# Populate data category table with Heart rate type
def populateDataCategoryTable():
    try:
        myCursor = db.cursor()
        dataCategory_insert_template = ("INSERT INTO DataCategory "
               "(data_category_name, is_time_series, has_subject_name, dc_table_name, dc_description) "
               "VALUE (%s, %s, %s, %s, %s)")

        # Add heart rate data category
        description = "Time series heart rate data collected by a FitBit Inspire HR"
        heart_rate_data_category = ('HeartRate', True, False, 'HeartRate_1', description)
        myCursor.execute(dataCategory_insert_template, heart_rate_data_category)
        db.commit()

        # Add Corsi data category
        description = "Test results from Corsi memory tests"
        corsi_data_category = ('Corsi', False, False, 'Corsi_1', description)
        myCursor.execute(dataCategory_insert_template, corsi_data_category)
        db.commit()

        # Add Flanker data category
        description = "Test results from Flanker attention tests"
        flanker_data_category = ('Flanker', False, False, 'Flanker_1', description)
        myCursor.execute(dataCategory_insert_template, flanker_data_category)
        db.commit()

        print("DataCategory Table populated successfully!")
    except mysql.connector.Error as e:
        print(e)
        print("ERROR: Issue Found When Populating DataCategory Table")

# Populate datacategory_study_xref table with Heart rate type and Exercise IQP
def populateDataCategoryStudyXrefTable():
    try:
        myCursor = db.cursor()
        dataCategoryStudyXref_insert_template = ("INSERT INTO DataCategoryStudyXref "
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
    except mysql.connector.Error as e:
        print(e)
        print("ERROR: Issue Found When Populating DataCategoryStudyXref Table")

# Populate heart rate table with 1 record for control subject 1 and 1 record for experimental subject 1
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
    except mysql.connector.Error as e:
        print(e)
        print("ERROR: Issue Found When Populating HeartRate Table")


# Populate attribute table with info for every column in the HeartRate, Corsi, and Flanker tables
def populateAttributeTable():
    try:
        myCursor = db.cursor()
        attribute_insert_template = ("INSERT INTO Attribute "
                   "(attr_name, data_type, data_category_id) "
                   "VALUE (%s, %s, %s)")

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
    except mysql.connector.Error as e:
        print(e)
        print("ERROR: Issue Found When Populating Attribute Table")


# should be removed once we add functionality for determining study automatically, either through analyzing files/folders or having the user specify
populateStudyTable()

# should be removed once we add functionality for determining samples automatically, either through analyzing files/folders or having the user specify
populateStudyGroupTable()

# should be removed once we add functionality for determining data types automatically, either through analyzing files/folders or having the user specify
populateDataCategoryTable()

# should be removed once we add functionality for associating projects with data types automatically, either through analyzing files/folders or having the user specify
populateDataCategoryStudyXrefTable()

populateAttributeTable()

db.close()