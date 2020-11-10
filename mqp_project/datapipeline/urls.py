from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='datapipeline-home'),
    path('studySelection/', views.studySelection, name='datapipeline-studySelection'),
    path('dataSelection/', views.dataSelection, name='datapipeline-dataSelection'),
    path('dataSelection-2/', views.dataSelectionContinued, name='datapipeline-dataSelection-2'),
    path('output', views.output, name='datapipeline-output'),
    path('uploader/', views.uploader, name='datapipeline-uploader'),
]
