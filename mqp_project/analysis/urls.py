from django.urls import path
from . import views

urlpatterns = [
    path('make_hist/', views.make_hist, name='analysis-make_hist'),
    path('show_hist/', views.show_hist, name='analysis-show_hist'),
    path('make_scatter/', views.make_scatter, name='analysis-make_scatter'),
    path('show_scatter/', views.show_scatter, name='analysis-show_scatter'),
]
