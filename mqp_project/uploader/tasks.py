from celery import shared_task
from celery_progress.backend import ProgressRecorder
import time

from django.conf import settings

from .viewHelpers import Helper, Handler
from .models import Document

@shared_task(bind=True)
def ProcessUpload(self, filenames, uploaderInfo, positionInfo, specialFlag):
    
    columnInfo = []
    organizedColumns = []
    
    progress_recorder = ProgressRecorder(self)
    
    noError = True 
    errorMessage = None
        
    numOfFiles = len(filenames) + 0.5
    directory_path = 'uploaded_csvs/'

    print('Task started')
    
    print('Start')
    for i, file in enumerate(filenames):
        filepath = directory_path + file
        print(filepath)
        if i == 0:
            columnInfo, organizedColumns = Helper.getInfo(positionInfo)
            i += 0.5
            progress_recorder.set_progress(i, numOfFiles, description="Uploading")

        if specialFlag is True: 
            print('Starting...')
            noError, errorMessage = Handler.specialUploadToDatabase(filepath, file, uploaderInfo, columnInfo)
            
        else:
            noError, errorMessage = Handler.uploadToDatabase(filepath, file, uploaderInfo, columnInfo, organizedColumns)
                
        if noError is False:
            raise Exception(errorMessage)
        
        else:
            #newdoc = Document.objects.create(uploadedFile=filepath, filename=file)
            Helper.deleteFile(filepath)
        # Sleep for 1 second
        time.sleep(0.1)
        
        progress_recorder.set_progress(i, numOfFiles, description="Uploading")
        
        
    return 'Upload was successful'

        
    