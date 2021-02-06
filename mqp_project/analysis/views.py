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


def make_hist(request):
    attribute_names = []
    if 'attribute_names' in request.session:
        attribute_names = request.session['attribute_names']

    if request.method == 'POST':
        attributes_form = CreateChosenBooleanForm(
            request.POST, customFields=request.session['attribute_names'])
        # process the data
        attribute_data = {}
        if attributes_form.is_valid():
            for i, field in enumerate(attributes_form.getAllFields()):
                if i == 0:
                    attribute_data[i] = {
                        # flipped these values to make the dict indexing work, will need to change
                        'name': field[1],
                        'value': 'bins'}
                else:
                    attribute_data[i] = {
                        'name': attribute_names[i-1],
                        'value': field[1]}
        # could we change this to  just get the dict and not the namelist?
        hist_data = ViewHelper.getNameList(attribute_data)
        request.session['hist_data'] = hist_data
        return HttpResponseRedirect('/analysis/show_hist')
    radio_choices = ViewHelper.getRadioChoices(request.session['attribute_names'])
    attributes_form = CreateChosenBooleanForm(
        customFields=radio_choices)
    context = {"hist_fields": attributes_form}
    return render(request, 'analysis/selectHistColumns.html', context)


def show_hist(request):
    # create dataframe based on previous query
    engine = sql.create_engine(settings.DB_CONNECTION_URL)
    df = pd.read_sql_query(sql=buildQuery(
        request.session['args']), con=engine)
    # adjust column name from front end selection (remove study label)
    col_name = request.session['hist_data'][1]
    
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


def make_scatter(request):
    attribute_names = []
    if 'attribute_names' in request.session:
        attribute_names = request.session['attribute_names']

    if request.method == 'POST':
        attributes_form = CreateChosenBooleanFormNoBins(
            request.POST, customFields=request.session['attribute_names'])
        # process the data
        attribute_data = {}
        if attributes_form.is_valid():
            for i, field in enumerate(attributes_form.getAllFields()):
                attribute_data[i] = {
                    'name': attribute_names[i],
                    'value': field[1]}
        # could we change this to  just get the dict and not the namelist?
        scatter_data = ViewHelper.getNameList(attribute_data)
        request.session['scatter_data'] = scatter_data
        return HttpResponseRedirect('/analysis/show_scatter')

    radio_choices = ViewHelper.getRadioChoices(request.session['attribute_names'])
    x_form = CreateChosenBooleanFormNoBins(
        customFields=radio_choices)
    y_form = CreateChosenBooleanFormNoBins(
        customFields=radio_choices)
    context = {"scatter_fields_x": x_form,
                "scatter_fields_y": y_form}
    return render(request, 'analysis/selectScatterColumns.html', context)


def show_scatter(request):
    engine = sql.create_engine(settings.DB_CONNECTION_URL)
    df = pd.read_sql_query(sql=buildQuery(request.session['args']), con=engine)
    xcol_name = request.session['scatter_data'][0]
    xcol_list = xcol_name.split('.')
    xcol = xcol_list[1]

    ycol_name = request.session['scatter_data'][1]
    ycol_list = ycol_name.split('.')
    ycol = ycol_list[1]

    # scatter plot
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


# user clarification for datatype
# TODO: change print statement to an alert/prompt


def clarifyDataType(dt):
    if dt == np.object:
        print('\nDatatype Clarification\n'
              '[1] String / text\n'
              '[2] Integer\n'
              '[3] Float / Decimal\n'
              '[4] Datetime\n\n'
              'Please type 1, 2, 3 or 4\n')

        myDt = int(input('\nEnter this column\'s Datatype: '))

        return myDt

    elif np.issubdtype(dt, np.datetime64):
        return 4

    return -1

# data type validation for scatter plots
# TODO: change print statements to alerts


def validateColsDataType(col, axis, df, dateFlag, myList):
    dataType = df[col].dtypes

    exactType = clarifyDataType(dataType)

    if exactType == 1:
        print("Can't Use String!")
        sys.exit(1)

    elif exactType == 4:
        dateFlag = True
        myList.append(axis)
        name = 'timestamp_{}'.format(axis)
        df[name] = pd.to_datetime(df[col]).apply(lambda date: date.timestamp())

        col = name

    return col, df, dateFlag, myList
