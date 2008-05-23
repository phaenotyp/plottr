from django.conf.urls.defaults import *
from django.views.generic import list_detail

from apps.dates.models import Date

urlpatterns = patterns('plotter.apps.dates.views',


    # redirect takes date, country and zip as get-parameters 
    # and redirects to the according url
    (r'redirect/', 'redirect' ), 

    # displays a input form for new dates.
    (r'new/', 'newdate' ), 
  
    # dates filtered by date and country
    # plottr.de/dates/2008-07/de/
    (r'(?P<date>[-\w]+)/(?P<country>[a-z]{2})/$', 'by_place'),

    # dates filtered by date, country & zipcode,  shortened zipcodes should be treated as wildcards
    # plottr.de/dates/2008-07/de/50672/
    # plottr.de/dates/today/de/50/
    (r'(?P<date>[-\w]+)/(?P<country>[a-z]{2})/(?P<zipcode>\d{1,5})/$', 'by_place'),

    # same as above but with several zips
    #plottr.de/dates/2008-07/de/50672,50675,50676/
                                              # this grouping could be problematic
    (r'(?P<date>[-\w]+)/(?P<country>[a-z]{2})/(?P<zipcode>\d{5}(,\d{5})+)/$', 'by_place'),

 
    # date filtered by date and geocoordinates and distance 
    # plottr.de/dates/today/1.231233,2.34234/walking/   
    # plottr.de/dates/tommorrow/1.231233,2.34234/5km/   
    (r'(?P<date>[-\w]+)/(?P<geo>[THISNEEDSAREGEX])/(?P<distance>\w+)/$', 'by_geo'),

    # one single date
    # plottr.de/dates/1234/
    url(r'id/(?P<id>\d+)/$', 'single_by_id', name='single_by_id'),

     
    # this is an older, more verbose version of the url of a single
    # date, maybe there should be a version with the slug 
    # for pretty links. 
    # one single date
    # plottr.de/dates/2008-04-14/click-clack-club/     
#    url(r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
 #      'single',
#       name='single'
#    ),

    # dates filtered by date 
    # plottr.de/dates/2008-04-14/
    # plottr.de/dates/2008/ 
    # plottr.de/dates/today/  
    (r'(?P<date>[-\w]+)/$', 'by_date' ),



    # a list of all dates 
    # a generic view is used but it's wrapped in a custom-view to allow 
    # content-negotiation. 
    # plottr.de/dates/
    ('$', 'date_list' ), 
)

 
