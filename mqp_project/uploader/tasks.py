from celery import shared_task
from celery_progress.backend import ProgressRecorder
import time

from django.conf import settings

from .viewHelpers import Helper
from datapipeline.models import DataCategory
from datapipeline.database import DBClient
from .models import Document
import jsonpickle

@shared_task(bind=True)
def ProcessUpload(self, filenames, uploaderInfo, positionInfo, specialFlag):
    
    uploaderInfo = jsonpickle.decode(uploaderInfo)
    columnInfo = []
    organizedColumns = []
    
    progress_recorder = ProgressRecorder(self)
    
    noError = True 
    errorMessage = None
    
    dcID = uploaderInfo.dcID
    
    dcObj = DataCategory.objects.get(data_category_id=dcID)
    numOfFiles = len(filenames) + 0.5
    directory_path = 'uploaded_csvs/'

    print('Task started')
    
    print('Start')
    
    for i, file in enumerate(filenames):
        filepath = directory_path + file
        
        newdoc = None
        
        if uploaderInfo.documentExists(file) is False:
            newdoc = Document.objects.create(filename=file, data_category=dcObj)
        
        docID = (Document.objects.get(filename=file, data_category=dcObj)).id
        
        if uploaderInfo.handleDuplicate == 'replace':
            DBClient.deleteData(uploaderInfo.tableName, docID)
            
        
        print(filepath)
        if i == 0:
            columnInfo, organizedColumns = Helper.getInfo(positionInfo)
            i += 0.5
            progress_recorder.set_progress(i, numOfFiles, description="Uploading")

        if specialFlag is True: 
            print('Starting...')
            noError, errorMessage = uploaderInfo.specialUploadToDatabase(filepath, docID, columnInfo) 
            
        else:
            noError, errorMessage = uploaderInfo.uploadToDatabase(filepath, file, docID, columnInfo, organizedColumns)
                
        if noError is False:
            if newdoc is not None:
                newdoc.delete()
                
            raise Exception(errorMessage)
        
        else:
            Helper.deleteFile(filepath)
        
        # Sleep for 1 second
        time.sleep(0.1)
        
        progress_recorder.set_progress(i, numOfFiles, description="Uploading")
        
        
    return 'Upload was successful'

        
    