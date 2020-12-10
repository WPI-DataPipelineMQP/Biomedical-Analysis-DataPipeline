from django.shortcuts import render
from django.conf import settings
from datapipeline.database import DBClient, DBHandler
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import numpy as np
import csv
import sys

# main analysis function
# TODO: connect to plotting functions create selection prompt


def data_analysis(request):
    # crerate sql connector engine and read session  query to dataframe
    engine = create_engine(settings.DB_CONNECTION_URL)
    df = pd.read_sql_query(sql=DBClient.buildQuery(request.args), con=engine)

    return render(request, 'analysis/dataAnalysis.html')


def create_histogram(df, col_choice):
    hist = df.hist(column=col_choice)
    plt.show(hist)


def create_scatter(df, xcol, ycol):
    dateAxis = []
    dateFlag = False

    # data type checker, will need to setup w/ input params from selection interface
    xcol, df, dateFlag, dateAxis = validateColsDataType(
        xcol, 'x', df, dateFlag, dateAxis)
    ycol, df, dateFlag, dateAxis = validateColsDataType(
        ycol, 'y', df, dateFlag, dateAxis)

    # scatter plot
    fig, ax = plt.subplots()
    ax.scatter(x=df[xcol], y=df[ycol])

    if dateFlag is True:
        if 'x' in dateAxis:
            locs, labels = plt.xticks()
            new_labels = [datetime.fromtimestamp(
                int(item)) for item in list(locs)]
            ax.set_xticklabels(new_labels)

        if 'y' in dateAxis:
            locs, labels = plt.yticks()
            new_labels = [datetime.fromtimestamp(
                int(item)) for item in list(locs)]
            ax.set_yticklabels(new_labels)

    plt.title(xcol + ' vs. ' + ycol)
    plt.xlabel(xcol)
    plt.ylabel(ycol)
    plt.show()


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
