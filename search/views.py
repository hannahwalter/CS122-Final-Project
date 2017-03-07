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



def _valid_result(res):
    """
    Validates results returned by give_recommendations
    which is expected to be of the format:
    [['Buy', confidence level (float based on sentiment index)],
     ['Neutral', confidence level],
     ['Sell', confidence level]]
    """
    for i in range(0, 3):
        if not isinstance(res[i][0], str):
            return False
        if not isinstance(res[i][1], float):
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
            if form.cleaned_data['company_name']:
                args['company_name'] = form.cleaned_data['company_name']
            if form.cleaned_data['date']:
                args['date'] = form.cleaned_data['date']
            if form.cleaned_data['investment_horizon']:
                args['investment_horizon'] = form.cleaned_data['investment_horizon']
            if form.cleaned_data['show_args']:
                context['args'] = 'args_to_ui = ' + json.dumps(args, indent=2)

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
    elif isinstance(res, str):
        context['result'] = None
        context['err'] = res
        result = None
    elif not _valid_result(res):
        context['result'] = None
        context['err'] = ('Return of fgive_recommendation has the wrong data type. '
                         'Should be a list of length 3 of [str, float]')
    else:
        result = res
        context['result'] = result
        context['num_results'] = len(result)
        context['columns'] = ['recommendation', 'confidence level']

    context['form'] = form
    return render(request, 'index.html', context)
