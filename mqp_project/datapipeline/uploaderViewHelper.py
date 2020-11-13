def extractName(string):
    indexPos = string.find('_')
    
    name = string[:indexPos]
    
    return name 

def getCleanFormat(myList):
    clean = []
    for (name, val) in myList:
        if '_custom_dataType' in name:
            colName = extractName(name)
            colName = colName.replace(" ", "")
            clean.append((colName, val))
    
    return clean 
    