from celery import shared_task
from celery_progress.backend import ProgressRecorder
import time

from django.conf import settings

from .viewHelpers import Helper, DBFunctions
from .models import Document

@shared_task(bind=True)
def ProcessUpload(self, filenames, uploaderInfo, positionInfo, specialFlag):
    
    columnInfo = []
    organizedColumns = []
    
    progress_recorder = ProgressRecorder(self)
    
    noError = True 
    errorMessage = None
        
    numOfFiles = len(filenames)
    directory_path = 'uploaded_csvs/'

    print('Task started')
    
    print('Start')
    for i, file in enumerate(filenames):
        filepath = directory_path + file
        print(filepath)
        if i == 0:
            columnInfo, organizedColumns = Helper.getInfo(positionInfo)
        
        if specialFlag is True:
            DBFunctions.specialUploadToDatabase(filepath, uploaderInfo, columnInfo)
            
        else:
            noError, errorMessage = DBFunctions.uploadToDatabase(filepath, file, uploaderInfo, columnInfo, organizedColumns)
                
        if noError is False:
            raise Exception(errorMessage)
        
        # Sleep for 1 second
        time.sleep(0.1)
        
        progress_recorder.set_progress(i, numOfFiles, description="Uploading")
        
    # DELETING UPLOADED CSV FILES
    try:
        for name in filenames:
            tmpPath = directory_path + name
            instance = Document.objects.get(uploadedFile=tmpPath, filename=name)
            instance.uploadedFile.delete()
            instance.delete()
            
            return 'Upload was successful'
            
    except:
        raise Exception('No Filenames!')
        
    