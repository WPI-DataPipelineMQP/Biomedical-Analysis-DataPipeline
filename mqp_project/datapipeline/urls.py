from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='datapipeline-home'),
    path('singleStudy/', views.singleStudy, name='datapipeline-singleStudy'),
    path('crossStudy/', views.crossStudy, name='datapipeline-crossStudy'),
]