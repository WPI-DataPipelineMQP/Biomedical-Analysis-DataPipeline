from django.urls import path
from . import views, uploaderViews

urlpatterns = [
    path('', views.home, name='datapipeline-home'),
    path('studySelection/', views.studySelection, name='datapipeline-studySelection'),
    path('dataSelection/', views.dataSelection, name='datapipeline-dataSelection'),
    path('dataSelection-2/', views.dataSelectionContinued, name='datapipeline-dataSelection-2'),
    path('output', views.output, name='datapipeline-output'),
    path('uploaderStudyName/', uploaderViews.uploaderStudyName, name='datapipeline-uploaderStudyName'),
    path('uploaderInfo/', uploaderViews.uploaderInfoGathering, name='datapipeline-uploaderInfo'),
    path('uploaderExtraInfo/', uploaderViews.uploaderExtraInfo, name='datapipeline-uploaderExtraInfo'),
    path('uploaderFinalPrompt/', uploaderViews.uploaderFinalPrompt, name='datapipeline-uploaderFinalPrompt'),
    path('uploader/', uploaderViews.uploader, name='datapipeline-uploader'),
]
