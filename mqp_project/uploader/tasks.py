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
    print(dcID)
    dcObj = DataCategory.objects.get(data_category_id=dcID)
    numOfFiles = len(filenames) + 0.5
    directory_path = settings.UPLOAD_PATH

    print('Task started')
    
    print('Start')
    
    for i, file in enumerate(filenames):
        
        newdoc = None
        
        if uploaderInfo.documentExists(file) is False:
            newdoc = Document.objects.create(filename=file, data_category=dcObj)
        
        docID = (Document.objects.get(filename=file, data_category=dcObj)).id
        
        if uploaderInfo.handleDuplicate == 'replace':
            DBClient.deleteData(uploaderInfo.tableName, docID)
            
        
        if i == 0:
            columnInfo, organizedColumns = Helper.getInfo(positionInfo)
            i += 0.5
            progress_recorder.set_progress(i, numOfFiles, description="Uploading...")
            
        df = Helper.getDataFrame(file)
        if specialFlag is True: 
            print('Starting...')
            noError, errorMessage = uploaderInfo.specialUploadToDatabase(df, docID, columnInfo) 
            
        else:
            noError, errorMessage = uploaderInfo.uploadToDatabase(df, file, docID, columnInfo, organizedColumns)
                
        if noError is False:
            if newdoc is not None:
                newdoc.delete()
                
            raise Exception(errorMessage)
        
        else:
            Helper.deleteFile(file) 
                   
        # Sleep for 1 second
        time.sleep(0.1)
        
        progress_recorder.set_progress(i, numOfFiles, description="Uploading")
        
        
    return 'Upload was successful'

        
    