from django.urls import path, include
from django.conf.urls import url
from . import views

urlpatterns = [
    path('study/', views.study, name='uploader-uploaderStudy'),
    path('studyInfo', views.studyInfo, name='uploader-uploaderStudyInfo'),
    path('info/', views.info, name='uploader-uploaderInfo'),
    path('extraInfo/', views.extraInfo, name='uploader-uploaderExtraInfo'),
    path('finalPrompt/', views.finalPrompt, name='uploader-uploaderFinalPrompt'),
    path('uploading/', views.upload, name='uploader-uploading'),
    path('error/', views.error, name='uploader-uploaderError'),
    path('success/', views.success, name='uploader-uploaderSuccess'),
    url(r'^s3direct/', include('s3direct.urls'))
]