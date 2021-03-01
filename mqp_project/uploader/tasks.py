from celery import shared_task
from celery_progress.backend import ProgressRecorder
import time

from django.conf import settings

from .viewHelpers import Helper
from datapipeline.models import DataCategory
from datapipeline.database import DBClient
from .models import Document
import jsonpickle

###
# Description: handles the actual uploading to the database. By defining it as a task, it allows the action to be done asynchronously
# PARAMS: filenames (String), uploaderInfo (UploaderInfo), positionInfo (Dictionary), specialFlag (Boolean)
# RETURN: String - a simple message saying the upload was successful (if True)
###
@shared_task(bind=True, max_retries=10)
def ProcessUpload(self, filenames, uploaderInfo, positionInfo, specialFlag):
    
    uploaderInfo = jsonpickle.decode(uploaderInfo)
    columnInfo = []
    organizedColumns = []
    
    progress_recorder = ProgressRecorder(self)
    
    noError = True 
    errorMessage = None
    
    dcID = uploaderInfo.dcID

    dcObj = DataCategory.objects.get(data_category_id=dcID)
    numOfFiles = len(filenames) + 0.5   # adds the 0.5 to account for the initial indicator that is automatically added to progress bar
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
            i += 0.5    # adds 0.5 to get the progress bar starting rather than start it at 0 (no progress shows at 0)
            progress_recorder.set_progress(i, numOfFiles, description="Uploading...")   # updates the progress bar on the client side
        
        
        df = Helper.getDataFrame(file)
        
        if df is None:
            raise Exception(f"S3 Key: {file} Not Found!")
        
        if specialFlag is True: 
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
        
        progress_recorder.set_progress(i, numOfFiles, description="Uploading...")  # updates the progress bar on the client side
        
        
    return 'Upload was successful'

        
    