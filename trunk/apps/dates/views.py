from django.views.generic.list_detail import object_list
from django.shortcuts import get_object_or_404, render_to_response
from django.core import serializers
from django.http import HttpResponse

from plotter.apps.dates.models import Date
from datetime import datetime, timedelta



def single(request, year, month, day, slug): 
    """One single date.
       /dates/2008/03/17/domingo-club/
    """
    date = get_object_or_404(Date.objects.by_date('%s-%s-%s'%(year,month,day)),slug=slug) 

    if request.accepts('text/html'):
        return render_to_response('dates/single.html', {'object': date})
      
    if request.accepts('application/json'):    
        return  HttpResponse(date.as_json(), mimetype='application/json') 

    if request.accepts('application/ical'):    
        return  HttpResponse(date.as_ical(), mimetype='application/ical') 
    

#TODO check if the following funtions can be reasonably refactored 
def by_date(request, date):
    """ a list of dates, matching the parameter date"""
   # we're using the generic view with custom parameters
    return object_list(   
       request,
       queryset = date.objects.by_date(date),
       template_name='dates/list.html',
       template_object_name='dates'
    )     

def by_place(request, date, place):
    """ a list of dates, matching the parameter date and place"""
   # we're using the generic view with custom parameters
    return object_list(   
       request,
       queryset = date.objects.by_date_and_place(date, place),
       template_name='dates/list.html',
       template_object_name='dates'
    )     


def by_geo(request, date, geo, distance):
    """Dates filtered by geocoordinates
       /dates/today/50.94918,6.98533/walking/
    """ 
    # wickedness
    pass





