from django.urls import path
from . import views

urlpatterns = [
    path('study/<str:id>/', views.studySummary, name='inventory-study'),
    # path('/', views.listStudies, name='inventory-listStudies'),
]