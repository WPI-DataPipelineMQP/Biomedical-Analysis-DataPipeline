from celery import shared_task
from celery_progress.backend import ProgressRecorder
import time

from django.conf import settings

from .viewHelpers import Helper, Handler
from datapipeline.models import DataCategory
from datapipeline.database import DBClient
from .models import Document

@shared_task(bind=True)
def ProcessUpload(self, filenames, uploaderInfo, positionInfo, specialFlag):
    
    columnInfo = []
    organizedColumns = []
    
    print(uploaderInfo)
    progress_recorder = ProgressRecorder(self)
    
    noError = True 
    errorMessage = None
    
    dcID = uploaderInfo.get('dcID')
    
    dcObj = DataCategory.objects.get(data_category_id=dcID)
    numOfFiles = len(filenames) + 0.5
    directory_path = 'uploaded_csvs/'

    print('Task started')
    
    print('Start')
    for i, file in enumerate(filenames):
        filepath = directory_path + file
        
        newdoc = None
        if Handler.documentExists(file, uploaderInfo.get('categoryName'), uploaderInfo.get('isTimeSeries'), uploaderInfo.get('studyID')) is False:
            newdoc = Document.objects.create(filename=file, data_category=dcObj)
        
        docID = (Document.objects.get(filename=file, data_category=dcObj)).id
        
        if uploaderInfo.get('handleDuplicate') == 'replace':
            DBClient.deleteData(uploaderInfo.get('tableName'), docID)
            
        
        print(filepath)
        if i == 0:
            columnInfo, organizedColumns = Helper.getInfo(positionInfo)
            i += 0.5
            progress_recorder.set_progress(i, numOfFiles, description="Uploading")

        if specialFlag is True: 
            print('Starting...')
            noError, errorMessage = Handler.specialUploadToDatabase(filepath, docID, uploaderInfo, columnInfo)
            
        else:
            noError, errorMessage = Handler.uploadToDatabase(filepath, file, docID, uploaderInfo, columnInfo, organizedColumns)
                
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

        
    