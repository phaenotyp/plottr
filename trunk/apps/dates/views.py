from django.views.generic.list_detail import object_list
from django.shortcuts import get_object_or_404, render_to_response
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect

from plotter.apps.dates.models import Date
from plotter.utils import json_encode
from datetime import datetime, timedelta 
from datetime import date as ddate
from django import newforms as forms


#  this is the form, that is displayed when javascript is not activated.
class QueryFallbackForm(forms.Form):
    date = forms.CharField(max_length=10, required=False)
    country = forms.ChoiceField( required=False, choices=(('de','de'), ('none','keins')))
    zips = forms.CharField(required=False)

    #def clean_zips():

    #def clean_date():
    #   ddate( ) 

    def get_url(self):
        if self.is_valid():
            url = '/dates/'
            if self.cleaned_data['date']:
                url += self.cleaned_data['date'] + '/'
                if self.cleaned_data['date']:
                    url += self.cleaned_data['country'] + '/'
                    if self.cleaned_data['zips']:
                        url += self.cleaned_data['zips'] + '/'
            return url
        else:
            raise  ValueError, 'Invalid Data in QueryFallbackForm'

#  takes a request with the parametera
#  date, country, zips 
#  and redirects to the corresponding url
def redirect( request ):
    form = QueryFallbackForm(request.REQUEST)
    try:
        return HttpResponseRedirect(form.get_url())
    except ValueError:
        return object_list(
           request,
           queryset = Date.objects.published(),
           template_name='dates/list.html',
           template_object_name='dates',
           extra_context={'queryfallbackform': form,'erro': 'No Matching Dates.' },
        )

# the views that retrn a single date.
def single_response(request, date):
    """Takes a single date and generates a response for it based on accept header"""
    if request.accepts('application/ical'):
        return  HttpResponse(date.as_ical(), mimetype='application/ical')

    if request.accepts('application/json'):
        return  HttpResponse(date.as_json(), mimetype='application/json')

    if request.accepts('text/html'):
        return render_to_response('dates/single.html', {'object': date, 'queryfallbackform': QueryFallbackForm()})

def single(request, year, month, day, country, zipcode, slug):
    """One single date.
       /dates/2008-03-17/domingo-club/
    """
    #TODO work country and zipcode into the queryset
    date = get_object_or_404(Date.objects.by_date('%s-%s-%s'%(year,month,day)),slug=slug)
    return single_response(request, date)

def single_by_id(request, id):
    """One single date.
       /dates/2345/
    """
    date = get_object_or_404(Date.objects.all(),pk=id)
    return single_response(request, date)

  

def date_list(request):
    """ a list of all dates
    """
    if request.accepts('application/json'):    
        dates = Date.objects.published()  
        for d in dates:
            d.de_normalize() 
        return  HttpResponse(json_encode(dates), mimetype='application/json') 
       

    if request.accepts('text/html'):
        # using the generic view with custom parameters
        return object_list(
           request,
           queryset = Date.objects.published(),
           template_name='dates/list.html',
           template_object_name='dates',
           extra_context = {'queryfallbackform': QueryFallbackForm()},
        )

#TODO check if the following funtions can be reasonably refactored 
def by_date(request, date):
    """ a list of dates, matching the parameter date
        /dates/2009-12-23/
    """
    dates = Date.objects.by_date(date)  
    if request.accepts('application/json'):    
        for d in dates:
            d.de_normalize() 
        return  HttpResponse(json_encode(dates), mimetype='application/json') 
 

    if request.accepts('text/html'):
        # using the generic view with custom parameters
        return object_list(   
           request,
           queryset = dates,
           template_name='dates/list.html',
           template_object_name='dates',
           extra_context ={'queryfallbackform': QueryFallbackForm({'date':date})},
        )     

def by_place(request, date, country, zipcode=None):
    """ a list of dates, matching the parameter date and place
        /dates/2009-12-23/de-52123/
    """

    # get dates by dates and country
    dates = Date.objects.by_date(date).filter(adress__country__iexact=country)
    # filter the queryset by zipcode
    if zipcode:
        # if several zipcodes are passed, seperated by commata
        if ',' in zipcode:
           zips = zipcode.split(',')
           #TODO this needs rewriting. 
           # not before queryset-refactor hits trunk
           dates = dates.filter(adress__zipcode__in=zips)
        # if a single or partial zipcode is passed
        else:
           dates = dates.filter(adress__zipcode__istartswith=str(zipcode))

    if request.accepts('application/json'):
        # denormalization to avoid an abundance of requests.
        # ForeignKey-Fields get serialized only by their id
        # so they are copied to be serialized like a normal object.
        for d in dates:
            d.de_normalize() 
        return HttpResponse(json_encode(dates), mimetype='application/json')

    if request.accepts('text/html'):
        # using the generic view with custom parameters
        return object_list(
           request,
           queryset = dates,
           template_name='dates/list.html',
           template_object_name='dates',
           extra_context ={'queryfallbackform': QueryFallbackForm({'date': date, 'country': country, 'zips': zipcode})},
        )

def by_geo(request, date, geo, distance):
    """Dates filtered by geocoordinates
       /dates/today/50.94918,6.98533/walking/
    """ 
    # wickedness
    pass
