from django.shortcuts import render
from django import forms
import json
import traceback
import sys
from create_output import create_output
import datetime
import pandas as pd
from django.forms.extras.widgets import SelectDateWidget

'''
def create_output(d):
    return {'bag_of_words': [['Positive words', '57%', '43%', '23%'], 
    ['Negative words', '43%', '57%', '77%'], ['Recommendation', 'Buy', 'Buy', 'Hold']],
    'top_words': [['1', 'a', 'b', 'c'], ['2', 'a', 'b', 'c'], ['3', 'a', 'b', 'c'],
    ['4', 'a', 'b', 'c'], ['1', 'a', 'b', 'c'], ['1', 'a', 'b', 'c'], ['1', 'a', 'b', 'c']
    , ['1', 'a', 'b', 'c'], ['1', 'a', 'b', 'c']],
    'bag_of_words_error': ['Could not find articles for NYTimes'],
    'monte_carlo': [['Dates', 'date1', 'date2'], ['Monte Carlo Values', 'value1', 'value2'], ['Stock Values', 'value1', 'value2']],
    'naive_bayes': [['Positive articles', 'x%', 'x%', 'x%'], ['Negative articles', 'y%', 'y%', 'y%']]}
'''

class SearchForm(forms.Form):
    company_name = forms.CharField(
            label='Key word(s) in company name or ticker',
            help_text='e.g. Apple, AAPL, AAP, Apple Computer Inc',
            required=True)
    date = forms.DateField(
            label='Date to look for recommendation',
            widget=SelectDateWidget(years = [2016, 2017]),
            initial=datetime.date.today(),
            required=True)
    days = forms.IntegerField(label = 'Number of days to scrape before date',
            required = True, max_value = 30, min_value = 1)
    show_args = forms.BooleanField(label='Show args_to_ui',
                                   required=False)
    bag_of_words = forms.BooleanField(label='Show Bag of Words',
                                    required=False)
    monte_carlo = forms.BooleanField(label='Show Monte Carlo',
                                    required=False)
    advanced_sentiment = forms.BooleanField(label='Show Advanced Sentiment Analysis',
                                    required=False)

def home(request):
    context = {}
    res = None
    if request.method == 'GET':
        form = SearchForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            # Convert form data to an args dictionary for create_output
            args = {}
            args['company_name'] = form.cleaned_data['company_name']
            args['date'] = form.cleaned_data['date'].isoformat()
            args['days'] = form.cleaned_data['days']
            if form.cleaned_data['bag_of_words']:
                args['bag_of_words'] = True
            else:
                args['bag_of_words'] = False
            if form.cleaned_data['monte_carlo']:
                args['monte_carlo'] = True
            else:
                args['monte_carlo'] = False
            if form.cleaned_data['advanced_sentiment']:
                args['advanced_sentiment'] = True
            else:
                args['advanced_sentiment'] = False
            if form.cleaned_data['show_args']:
                context['args'] = 'args_to_ui:\n' + json.dumps(args, indent=4)

            try:
                res = create_output(args)
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
    else:
        context['recommendation'] = 'header'
        context.update(res)
    context['form'] = form
    
    return render(request, 'index.html', context)