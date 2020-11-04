from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='datapipeline-home'),
    path('singleStudy/', views.singleStudy, name='datapipeline-singleStudy'),
    path('crossStudy/', views.crossStudy, name='datapipeline-crossStudy'),
    path('dataSelection/', views.dataSelection, name='datapipeline-dataSelection'),
    path('dataSelection-2/', views.dataSelectionContinued, name='datapipeline-dataSelection-2'),
]