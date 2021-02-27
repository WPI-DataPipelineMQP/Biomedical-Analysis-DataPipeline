from django.shortcuts import render
from django.conf import settings
from datapipeline.database.DBClient import buildQuery
import sqlalchemy as sql
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import numpy as np
import csv
import sys
from datapipeline.viewHelpers import viewsHelper as ViewHelper
from .forms import *
from django.http import HttpResponseRedirect
import io
import urllib
import base64

# script for histogram prompt where user selects bin number and attribute
# calls session data from selection output
def make_hist(request):
    attribute_names = []
    if 'attribute_names' in request.session:
        attribute_names = request.session['attribute_names']

    if request.method == 'POST':
        attributes_form = CreateChosenBooleanForm(
            request.POST, customFields=request.session['radio_choices'])
        # process the data
        attribute_data = {}
        if attributes_form.is_valid():
            for i, field in enumerate(attributes_form.getAllFields()):
                if i == 0:
                    #bins
                    attribute_data[i] = {
                        # flipped these values to make the dict indexing work, will need to change
                        'name': field[1],
                        'value': 'bins'}
                else:
                    #attribute
                    attribute_data[i] = {
                        'name': field[1],
                        'value': 'attr'}
        hist_data = ViewHelper.getNameList(attribute_data)
        request.session['hist_data'] = hist_data
        return HttpResponseRedirect('/analysis/show_hist')
    radio_choices = ViewHelper.getRadioChoices(request.session['attribute_names'])
    request.session['radio_choices'] = radio_choices
    attributes_form = CreateChosenBooleanForm(
        customFields=radio_choices)
    context = {"hist_fields": attributes_form}
    return render(request, 'analysis/selectHistColumns.html', context)

# script for displaying histogram
# calls session data from make_hist
def show_hist(request):
    # create dataframe based on previous query
    engine = sql.create_engine(settings.DB_CONNECTION_URL)
    df = pd.read_sql_query(sql=buildQuery(
        request.session['args']), con=engine)
    # adjust column name from front end selection (remove study label)
    col_num = int(request.session['hist_data'][1])
    col_name = request.session['attribute_names'][col_num]
    
    if col_name.find('.') != -1:
        col_list = col_name.split('.')
        col_name = col_list[1]
        
    # turn column to np array
    as_array = df[col_name].to_numpy()
    # plot figure and save to django compatible format
    plt.hist(bins=request.session['hist_data'][0], x=as_array)
    plt.title(label='Distribution of ' + col_name)
    plt.xlabel(xlabel=col_name)
    plt.ylabel(ylabel='Frequency')
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return render(request, 'analysis/showHist.html', {'data': uri})

# script for scatter plot prompt where user selects attributes
# calls session data from selection output
def make_scatter(request):
    attribute_names = []
    if 'attribute_names' in request.session:
        attribute_names = request.session['attribute_names']

    if request.method == 'POST':
        attributes_form = CreateChosenBooleanFormScatter(
            request.POST, customFields=request.session['radio_choices'])
        # process the data
        attribute_data = {}
        if attributes_form.is_valid():
            for i, field in enumerate(attributes_form.getAllFields()):
                attribute_data[i] = {
                    'name': field[1],
                    'value': 'attr' + field[1]}
        # could we change this to  just get the dict and not the namelist?
        scatter_data = ViewHelper.getNameList(attribute_data)
        request.session['scatter_data'] = scatter_data
        return HttpResponseRedirect('/analysis/show_scatter')

    radio_choices = ViewHelper.getRadioChoices(request.session['attribute_names'])
    request.session['radio_choices'] = radio_choices
    attributes_form = CreateChosenBooleanFormScatter(
        customFields=radio_choices)
    context = {"scatter_fields": attributes_form}
    return render(request, 'analysis/selectScatterColumns.html', context)

# script for displaying scatter plot
# calls session data from make_scatter
def show_scatter(request):
    engine = sql.create_engine(settings.DB_CONNECTION_URL)
    df = pd.read_sql_query(sql=buildQuery(request.session['args']), con=engine)
    
    #format attribute names to be used as dataframe columns
    xcol_num = int(request.session['scatter_data'][0])
    xcol_name = request.session['attribute_names'][xcol_num]
    xcol_list = xcol_name.split('.')
    xcol = xcol_list[0]
    if len(xcol_list) > 1:
        xcol = xcol_list[1]

    ycol_num = int(request.session['scatter_data'][1])
    ycol_name = request.session['attribute_names'][ycol_num]
    ycol_list = ycol_name.split('.')
    ycol = ycol_list[0]
    if len(ycol_list) > 1:
        ycol = ycol_list[1]

    # scatter plot on django
    # url: https://medium.com/@mdhv.kothari99/matplotlib-into-django-template-5def2e159997
    plt.scatter(x=df[xcol], y=df[ycol])
    plt.title(xcol + ' vs. ' + ycol)
    plt.xlabel(xcol)
    plt.ylabel(ycol)
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.close()
    return render(request, 'analysis/showScatter.html', {'data': uri})

