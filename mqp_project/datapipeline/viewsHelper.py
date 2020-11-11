import json

def getJSONVersion(raw_list):
    dictionaries = []
    
    for raw_dict in raw_list:
        reformatted = str(raw_dict).replace("'", '"')
        study = json.loads(reformatted)
        dictionaries.append(study)
        
    return dictionaries
    
    
    