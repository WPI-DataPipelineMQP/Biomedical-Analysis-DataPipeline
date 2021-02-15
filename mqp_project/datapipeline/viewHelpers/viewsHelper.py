import json


def getJSONVersion(raw_list):
    dictionaries = []

    for raw_dict in raw_list:
        reformatted = str(raw_dict).replace("'", '"')
        study = json.loads(reformatted)
        dictionaries.append(study)

    return dictionaries


def getNameList(data, forStudy=False):
    res = []
    print('Data')
    print(data)
    print()
    for key in data:
        currDict = data.get(key)
        if currDict.get('value'):

            studyName = currDict.get('name')

            if forStudy is True:
                studyID = currDict.get('id')
                studyName += " (Study ID = {})".format(studyID)

            res.append(studyName)
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

def getRadioChoices(attributes):
    choices = []
    for i, attr in enumerate(attributes):
        tup = (i, attr)
        choices.append(tup)
    return choices
