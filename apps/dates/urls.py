from django.conf.urls.defaults import *
from django.views.generic import list_detail

from apps.dates.models import Date

urlpatterns = patterns('plotter.apps.dates.views',

    # one single date
    # plottr.de/dates/2008-04-14/click-clack-club/     
    url(r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
       'single',
       name='single'
    ),

    # dates filtered by date 
    # plottr.de/dates/2008-04-14/
    # plottr.de/dates/2008/ 
    # plottr.de/dates/today/  
    (r'(?P<date>[-\w]+)/$', 'by_date' ),

    # dates filtered by date and place 
    # plottr.de/dates/2008-07/de-53175/
    # plottr.de/dates/all/koeln/   ?? 
    (r'(?P<date>[-\w]+)/(?P<place>[-\w]+)/$', 'by_place'),
    
    # date filtered by date and geocoordinates and distance 
    # plottr.de/dates/today/1.231233,2.34234/walking/   
    # plottr.de/dates/tommorrow/1.231233,2.34234/5km/   
    (r'(?P<date>[-\w]+)/(?P<geo>[THISNEEDSAREGEX])/(?P<distance>\w+)/$', 'by_geo'),

)

urlpatterns += patterns('',
   ('', list_detail.object_list, {'queryset': Date.objects.all(),  'template_name': 'dates/list.html', 'template_object_name': 'dates',} ),
) 
