from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='datapipeline-home'),
    path('study_selection/', views.studySelection, name='datapipeline-studySelection'),
    path('dataSelection/', views.dataSelection, name='datapipeline-dataSelection'),
    path('dataSelection-2/', views.dataSelectionContinued, name='datapipeline-dataSelection-2'),
    path('output', views.output, name='datapipeline-output'),
    path('export_data', views.export_data, name='datapipeline-export_data'),
    path('export_summary', views.export_summary, name='datapipeline-export_summary')
]
