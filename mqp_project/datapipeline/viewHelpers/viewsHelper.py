import json


def getJSONVersion(raw_list):
    dictionaries = []

    for raw_dict in raw_list:
        reformatted = str(raw_dict).replace("'", '"')
        study = json.loads(reformatted)
        dictionaries.append(study)

    return dictionaries

######################################
# Input: Dictionary, Boolean
# Returns: List
# Description: Gathers the list of names from the data produced by a dynamic boolean form
######################################
def getNameList(data, forStudy=False):
    res = []
    # print('Data')
    # print(data)
    # print()
    for key in data:
        currDict = data.get(key)
        #if the item was selected
        if currDict.get('value'):

            #add the name of the item
            name = currDict.get('name')

            #if it is a study, 
            if forStudy is True:
                studyID = currDict.get('id')
                name += " (Study ID = {})".format(studyID)

            #add to the list of names
            res.append(name)
    return res


def getChosenFilters(data):
    res = []

    for key in data:
        currDict = data.get(key)
        if currDict.get("value"):
            newDict = {}
            name = currDict.get('name')
            value = currDict.get('value')
            newDict['name'] = name
            newDict['value'] = value
            res.append(newDict)

    return res


def returnProperType(val):
    if val.isdigit():
        return val

    elif val.replace('.', '', 1).isdigit():
        return val

    else:
        stringVal = "'{}'".format(val)
        return stringVal

######################################
# Input: List
# Returns: List
# Description: Turns a list of names into a list of tuples with an auto-incrementing ID so it is compatible with a ChoiceField
######################################
def getRadioChoices(attributes):
    choices = []
    for i, attr in enumerate(attributes):
        tup = (i, attr)
        choices.append(tup)
    return choices
