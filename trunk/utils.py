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
