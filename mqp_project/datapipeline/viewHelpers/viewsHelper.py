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
