from django.shortcuts import render
from django import forms
import json
import traceback
import sys
from create_output import create_output
import datetime
from django.forms.extras.widgets import SelectDateWidget

class SearchForm(forms.Form):
    company_name = forms.CharField(
            label='Key word(s) in company name or ticker',
            help_text='e.g. Apple, AAPL, AAP, Apple Computer Inc',
            required=True)
    date = forms.DateField(
            label='Date to look for recommendation',
            widget=SelectDateWidget,
            initial=datetime.date.today(),
            required=True)
    show_args = forms.BooleanField(label='Show args_to_ui',
                                   required=False)
    bag_of_words = forms.BooleanField(label='Show bag of words',
                                    required=False)
    monte_carlo = forms.BooleanField(label='Show Monte Carlo',
                                    required=False)
    naive_bayes = forms.BooleanField(label='Show naive bayes',
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
            args['company_name'] = form.cleaned_data['company_name']
            args['date'] = form.cleaned_data['date'].isoformat()
            if form.cleaned_data['bag_of_words']:
                args['bag_of_words'] = True
            else:
                args['bag_of_words'] = False
            if form.cleaned_data['monte_carlo']:
                args['monte_carlo'] = True
            else:
                args['monte_carlo'] = False
            if form.cleaned_data['naive_bayes']:
                args['naive_bayes'] = True
            else:
                args['naive_bayes'] = False
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
        context['result'] = json.dumps(res, indent=8)
        if form.cleaned_data['monte_carlo']:
            context['image'] = True
        else:
            context['image'] = False
    context['form'] = form
    return render(request, 'index.html', context)