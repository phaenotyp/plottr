# -*- coding: utf-8 -*-
from plotter import settings

def static_map(params):
    """returns an url to a static-google-map
       takes a dictionary with parameters:
       params.long
       params.lat 
       params.zoom  1-19 ?? 
       params.maptype mobile|roadmap
       params.apikey
       params.markers an array of dictionaries { lat, long, color, char }    

       see:
       http://code.google.com/apis/maps/documentation/staticmaps/
    """ 

    # provide sensible defaults
    defaults = {
       'zoom': 14,
       'maptype': 'mobile',
       'height' : 200,
       'width'  : 200,
       'apikey' : settings.GOOGLE_API_KEY, 
    } 
 
    for key in defaults.iterkeys():
        params.setdefault(key,defaults[key])  

    # generate string for markers
    markerstr = '' 
    if 'markers' in params:
       markerstr = '&markers='
       ms = [] 
       for m in params['markers']: 
           # one marker: '{latitude},{longitude},{color}{alpha-character}'
           ms.append('%f,%f,%s%s' % (m['lat'], m['long'], m.get('color','red'), m.get('char',''))) 
       markerstr = '&markers=' + '|'.join(ms)
    params['markers'] = markerstr     
    

    url ="""http://maps.google.com/staticmap?center=%(lat)f,%(long)f&zoom=%(zoom)i&size=%(width)ix%(height)i&maptype=%(maptype)s%(markers)s&key=%(apikey)s""" 

    return url % params


def selection_description(date, country, zip=None): 
    """returns a string description of a selection of dates"""
    date = date.split('-')
    out = 'Termine'
    if len(date)==3:
        out += ' am %s.%s.%s' % (date[2],date[1],date[0])
    elif len(date)==2:
        monthnames = ' ,Januar,Februar,Maerz,April,Mai,Juni,Juli,August,September,Oktober,Noveber,Dezember'.split(',')
        out += ' im %s %s' % (monthnames[int(date[1])],date[0])
    else: 
        out += ' ' +str(date[0])
    if country and not zip:
        if country == 'de':
            out += ' in Deutschland'
    if zip: 
        zipmap = {
           (50667, 50668, 50670, 50672): u'Köln-Neustadt-Nord',
           (50823, 50825) : u'Köln-Neuehrenfeld', 
           (50679,) : u'Köln-Deutz', 
           (50935, 50937, 50939) : u'Köln-Sülz', 
           (50823, 50825) : u'Köln-Ehrenfeld',
           tuple(range(50441, 51149)) : u'Köln',
           tuple(range(53111, 53229)) : u'Bonn'
        }  
        matches = [] 
        checked = []
        for zipps in zipmap.keys(): 
            for zipp in zipps:
                if zipp not in checked and \
                   str(zipp).startswith(str(zip)) and \
                   zipmap[zipps] not in matches:
                    matches.append(zipmap[zipps]) 
                    checked.append(zipp) 
        hits = len(matches)
        if hits >= 3: 
            out += ' in ' + ', '.join(matches[0:-1]) + ' und ' + matches[hits-1] 
        elif hits == 2:
            out += ' in ' +  ' und '.join(matches)   
        elif hits == 1:
            out += ' in %s' %  matches[0] 
        elif len(str(zip)) < 5: 
            out += ' im Postleitzahlenbereich %s.' % str(zip) + '*'
        else:
            out += ' mit plz %s.'  % str(zip)
    return out
            
 




from decimal import Decimal
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.db import models
from django.utils.functional import Promise
from django.utils.encoding import force_unicode
from django.utils import simplejson as json


# http://wolfram.kriesing.de/blog/index.php/2007/json_encode-updated
# Wolfram Kriesings json encoder allows models to be modified 
# before being serialized to json.

def json_encode(data):
    """
    The main issues with django's default json serializer is that properties that
    had been added to an object dynamically are being ignored (and it also has 
    problems with some models).
    """

    def _any(data):
        ret = None
        # Opps, we used to check if it is of type list, but that fails 
        # i.e. in the case of django.newforms.utils.ErrorList, which extends
        # the type "list". Oh man, that was a dumb mistake!
        if isinstance(data, list):
            ret = _list(data)
        # Same as for lists above.
        elif isinstance(data, dict):
            ret = _dict(data)
        elif isinstance(data, Decimal):
            # json.dumps() cant handle Decimal
            ret = str(data)
        elif isinstance(data, models.query.QuerySet):
            # Actually its the same as a list ...
            ret = _list(data)
        elif isinstance(data, models.Model):
            ret = _model(data)
        # here we need to encode the string as unicode (otherwise we get utf-16 in the json-response)
        elif isinstance(data, basestring):
            ret = unicode(data)
        # see http://code.djangoproject.com/ticket/5868
        elif isinstance(data, Promise):
            ret = force_unicode(data)
        else:
            ret = data
        return ret
    
    def _model(data):
        ret = {}
        # If we only have a model, we only want to encode the fields.
        for f in data._meta.fields:
            ret[f.attname] = _any(getattr(data, f.attname))
        # And additionally encode arbitrary properties that had been added.
        fields = dir(data.__class__) + ret.keys()
        add_ons = [k for k in dir(data) if k not in fields]
        for k in add_ons:
            ret[k] = _any(getattr(data, k))
        return ret
    
    def _list(data):
        ret = []
        for v in data:
            ret.append(_any(v))
        return ret
    
    def _dict(data):
        ret = {}
        for k,v in data.items():
            ret[k] = _any(v)
        return ret
    
    ret = _any(data)
    
    return json.dumps(ret, cls=DateTimeAwareJSONEncoder)

