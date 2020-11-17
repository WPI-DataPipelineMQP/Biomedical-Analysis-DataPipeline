from django.urls import path
from . import views, uploaderViews

urlpatterns = [
    path('', views.home, name='datapipeline-home'),
    path('studySelection/', views.studySelection, name='datapipeline-studySelection'),
    path('dataSelection/', views.dataSelection, name='datapipeline-dataSelection'),
    path('dataSelection-2/', views.dataSelectionContinued, name='datapipeline-dataSelection-2'),
    path('output', views.output, name='datapipeline-output'),
    path('uploaderStudy/', uploaderViews.uploaderStudy, name='datapipeline-uploaderStudy'),
    path('uploaderStudyInfo', uploaderViews.uploaderStudyInfo, name='datapipeline-uploaderStudyInfo'),
    path('uploaderInfo/', uploaderViews.uploaderInfo, name='datapipeline-uploaderInfo'),
    path('uploaderExtraInfo/', uploaderViews.uploaderExtraInfo, name='datapipeline-uploaderExtraInfo'),
    path('uploaderFinalPrompt/', uploaderViews.uploaderFinalPrompt, name='datapipeline-uploaderFinalPrompt'),
    path('uploader/', uploaderViews.uploader, name='datapipeline-uploader'),
    path('uploaderError/', uploaderViews.uploaderError, name='datapipeline-uploaderError'),
]
