from django.conf.urls.defaults import *


# patterns for dates
urlpatterns = patterns('',
    # the url of the dates application are managed by itself
    (r'^dates/', include('plotter.apps.dates.urls')),
)

# patterns for events 
urlpatternsss = patterns('',
    # an overview of events per year
    # plottr.de/events/2008/
    # TODO replace by generic 

    (r'^events/(?P<year>\d{4})/$', 'plotter.apps.dates.views.events_year'), 

    # the dates of one single event 
    # plottr.de/events/2008/lit-cologne/
    (r'^events/(?P<year>\d{4})/(?P<slug>[-\w]+)/$', 'plotter.apps.dates.views.events_year'), 
)

urlpatterns += patterns('',
    # Uncomment this for admin:
    # plottr.de/admin/
    (r'^admin/', include('django.contrib.admin.urls')),
)

from plotter import settings

# this is for testing with the development server only 
if settings.DEVELOPMENT:
    urlpatterns += patterns('',
        (r'^sitemedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.LOCAL_MEDIA}),
    )
