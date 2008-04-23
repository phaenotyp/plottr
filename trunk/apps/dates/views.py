from django.views.generic.list_detail import object_list
from django.shortcuts import get_object_or_404, render_to_response
from django.core import serializers
from django.http import HttpResponse

from plotter.apps.dates.models import Date
from plotter.utils import json_encode
from datetime import datetime, timedelta


def single_response(request, date):
    """Takes a single date and generates a response for it based on accept header"""
    if request.accepts('application/ical'):
        return  HttpResponse(date.as_ical(), mimetype='application/ical')

    if request.accepts('application/json'):
        return  HttpResponse(date.as_json(), mimetype='application/json')

    if request.accepts('text/html'):
        return render_to_response('dates/single.html', {'object': date})

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
    """ a list of dates
    """
    if request.accepts('application/json'):    
        dates = Date.objects.published()  
        for d in dates:
            d.absolute_url = d.get_absolute_url() 
            d.adressdata = d.adress
            d.locationdata = d.location
        return  HttpResponse(json_encode(dates), mimetype='application/json') 
       

    if request.accepts('text/html'):
        # using the generic view with custom parameters
        return object_list(   
           request,
           queryset = Date.objects.published(),
           template_name='dates/list.html',
           template_object_name='dates'
        )     

#TODO check if the following funtions can be reasonably refactored 
def by_date(request, date):
    """ a list of dates, matching the parameter date
        /dates/2009-12-23/
    """
    

    dates = Date.objects.by_date(date)  
    if request.accepts('application/json'):    
        for d in dates:
            d.absolute_url = d.get_absolute_url() 
            d.adressdata = d.adress
            d.locationdata = d.location
        return  HttpResponse(json_encode(dates), mimetype='application/json') 
 

    if request.accepts('text/html'):
        # using the generic view with custom parameters
        return object_list(   
           request,
           queryset = dates,
           template_name='dates/list.html',
           template_object_name='dates'
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
           dates = dates.filter(adress__zipcode__in=zips)
        # if a single or partial zipcode is passed
        else:
           dates = dates.filter(adress__zipcode__istartswith=str(zipcode))

    if request.accepts('application/json'):
        # denormalization to avoid an abundance of requests.
        # ForeignKey-Fields get serialized only by their id
        # so they are copied to be serialized like a normal object.
        # TODO: move the denormalization into the model.
        for d in dates:
            d.absolute_url = d.get_absolute_url()
            d.adressdata = d.adress
            d.locationdata = d.location
        return HttpResponse(json_encode(dates), mimetype='application/json')

    if request.accepts('text/html'):
        # using the generic view with custom parameters
        return object_list(
           request,
           queryset = dates,
           template_name='dates/list.html',
           template_object_name='dates'
        )



def _by_place(request, date, country, zip=None):
    """ a list of dates, matching the parameter date and place
        /dates/2009-12-23/de-52123/
    """
    print 'place and date'
    dates = Date.objects.by_date_and_place(date, country, zip)
    if request.accepts('application/json'):    
        for d in dates:
            d.absolute_url = d.get_absolute_url() 
            d.adressdata = d.adress
            d.locationdata = d.location
        return  HttpResponse(json_encode(dates), mimetype='application/json') 
 
    if request.accepts('text/html'):
        # using the generic view with custom parameters
        return object_list(   
           request,
           queryset = dates,
           template_name='dates/list.html',
           template_object_name='dates'
        )     


def by_geo(request, date, geo, distance):
    """Dates filtered by geocoordinates
       /dates/today/50.94918,6.98533/walking/
    """ 
    # wickedness
    pass





