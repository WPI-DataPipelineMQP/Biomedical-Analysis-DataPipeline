import json

class ViewHelper():
    def getJSONVersion(self, raw_list):
        dictionaries = []
    
        for raw_dict in raw_list:
            reformatted = str(raw_dict).replace("'", '"')
            study = json.loads(reformatted)
            dictionaries.append(study)
        
        return dictionaries

    def getNameList(data):
    	res = []
    	for item in data:
    		if data[item]["value"]:
    			res.append(data[item]["name"])
    	return res

    
    