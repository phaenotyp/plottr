from django.views.generic.list_detail import object_list
from django.shortcuts import get_object_or_404, render_to_response
from django.core import serializers
from django.http import HttpResponse

from plotter.apps.dates.models import Date
from plotter.utils import json_encode
from datetime import datetime, timedelta


def single(request, year, month, day, slug): 
    """One single date.
       /dates/2008/03/17/domingo-club/
    """
    date = get_object_or_404(Date.objects.by_date('%s-%s-%s'%(year,month,day)),slug=slug) 

    date.description = request.META['HTTP_ACCEPT'] 

    if request.accepts('application/ical'):    
        return  HttpResponse(date.as_ical(), mimetype='application/ical') 
    
    if request.accepts('application/json'):    
        return  HttpResponse(date.as_json(), mimetype='application/json') 

    if request.accepts('text/html'):
        return render_to_response('dates/single.html', {'object': date})
   

def date_list(request):
    """ a list of dates
    """
    if request.accepts('application/json'):    
        dates = Date.objects.published()  
        for d in dates:
            d.absolute_url = d.get_absolute_url() 
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
        return  HttpResponse(json_encode(dates), mimetype='application/json') 
 

    if request.accepts('text/html'):
        # using the generic view with custom parameters
        return object_list(   
           request,
           queryset = dates,
           template_name='dates/list.html',
           template_object_name='dates'
        )     

def by_place(request, date, place):
    """ a list of dates, matching the parameter date and place
        /dates/2009-12-23/de-52123/
    """
    if request.accepts('application/json'):    
        for d in dates:
            d.absolute_url = d.get_absolute_url() 
        return  HttpResponse(json_encode(dates), mimetype='application/json') 
 
    if request.accepts('text/html'):
        # using the generic view with custom parameters
        return object_list(   
           request,
           queryset = Date.objects.by_date_and_place(date, place),
           template_name='dates/list.html',
           template_object_name='dates'
        )     


def by_geo(request, date, geo, distance):
    """Dates filtered by geocoordinates
       /dates/today/50.94918,6.98533/walking/
    """ 
    # wickedness
    pass





