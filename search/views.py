from django.shortcuts import render
from django.http import HttpResponse
from django import forms
import json
import traceback
from io import StringIO
import sys
import csv
import os
from operator import and_
# from give_recommendations import give_recommendations
from functools import reduce


def give_recommendations(company_name, date, graphical_analysis = False, numerical_analysis = False):
    return [[['Buy', .10], ['Neutral', .40], ['Sell', .35]], [['Positive sentiment', .776, .522], ['Negative sentiment', .283, .554]], ['/graphs/apple_1', '/graphs/apple_2']]

def _valid_result(res):
    """
    Validates results returned by give_recommendations
    which is expected to be of the format:
    [[['Buy', confidence level (float based on sentiment index)],
      ['Neutral', confidence level],
      ['Sell', confidence level]],
     [['Positive sentiment', positive_sentiment_index_from_Twitter, positive_sentiment_index_from_New_York_Times],
      ['Negative sentiment', negative_sentiment_index_from_Twitter, negative_sentiment_index_from_New_York_Times]],
     [graph_file_path_1, graph_file_path_2, ...]]
    """
    for i in range(0, 3):
        if not isinstance(res[0][i][0], str):
            return False
        if not isinstance(res[0][i][1], float):
            return False
    for j in range(0, 2):
        if not isinstance(res[1][j][0], str):
            return False
        if not isinstance(res[1][j][1], float):
            return False
        if not isinstance(res[1][j][2], float):
            return False
    for k in range(0, len(res[2])):
        if not isinstance(res[2][k], str):
            return False
    return True

def _valid_date(date):
    if not isinstance(date, str):
        return False
    if not date[4] == '-':
        return False
    if not date[6] == '-':
        return False
    return True

import datetime
from django.forms.extras.widgets import SelectDateWidget
from django.forms import ModelForm, Form

class SearchForm(forms.Form):
    company_name = forms.CharField(
            label='Key word(s) in company name or ticker',
            help_text='e.g. Apple, AAPL, AAP, Apple Computer Inc',
            required=True)
    date = forms.DateField(
            label='Date to look for recommendation',
            widget=SelectDateWidget,
            required=True)
    investment_horizon = forms.MultipleChoiceField(
            label='Investment_horizon',
            choices=[('days', 'a couple of days'), ('weeks', 'a couple of weeks'), ('months', 'a couple of months'), ('years', 'a couple of years')],
            widget=forms.CheckboxSelectMultiple,
            required=False)
    show_args = forms.BooleanField(label='Show args_to_ui',
                                   required=False)
    show_numerical_analysis = forms.BooleanField(label='Show numerical_analysis',
                                    required=False)
    show_graphical_analysis = forms.BooleanField(label='Show graphical_analysis',
                                    required=False)


def home(request):
    context = {}
    res = None
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():

            # Convert form data to an args dictionary for find_courses
            args = {}
            # if form.cleaned_data['company_name']:
            #     args['company_name'] = form.cleaned_data['company_name']
            if form.cleaned_data['date']:
                args['date'] = form.cleaned_data['date'].isoformat()
            if form.cleaned_data['investment_horizon']:
                args['investment_horizon'] = form.cleaned_data['investment_horizon']
            if form.cleaned_data['show_numerical_analysis']:
                args['numerical_analysis'] = form.cleaned_data['show_numerical_analysis']
            if form.cleaned_data['show_graphical_analysis']:
                args['graphical_analysis'] = form.cleaned_data['show_graphical_analysis']
            if form.cleaned_data['show_args']:
                context['args'] = 'args_to_ui:\n' + json.dumps(args, indent=4)

            try:
                res = give_recommendations(args)
            except Exception as e:
                print('Exception caught')
                bt = traceback.format_exception(*sys.exc_info()[:3])
                context['err'] = """
                An exception was thrown in give_recommendations:
                <pre>{}
{}</pre>
                """.format(e, '\n'.join(bt))

                res = None
    else:
        form = SearchForm()

    # Handle different responses of res
    if res is None:
        context['result'] = None
    elif not _valid_result(res):
        context['result'] = None
        context['err'] = ('Return of fgive_recommendation has the wrong data format. ')
    else:
        context['result'] = res[0:min(2, len(res))]
        if len(res) == 3:
            context['image'] = res[2]
        else:
            context['image'] = None

    context['form'] = form
    return render(request, 'index.html', context)