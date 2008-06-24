from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from geopy import geocoders
from plotter import settings
from plotter.utils import static_map
from plotter.apps.dates.managers import DateManager



COUNTRY_CHOICES = (
 ('de' , 'de'),
)

class Adress(models.Model):
    """Represents one Adress"""
    street  = models.CharField(max_length=100, blank=True)
    city    = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, choices=COUNTRY_CHOICES)
    zipcode = models.CharField(max_length=20, blank=True)
    lat     = models.FloatField(blank=True, null=True)
    long    = models.FloatField(blank=True, null=True)

    #location = models.ForeignKey('Location', edit_inline=models.STACKED, num_in_admin=1, blank=True, null=True, unique=True) # should be one-to-one 

    def get_json(self):
       """returns the adress as a json-object"""
       pass


    def __str__(self):
        return '%s, %s' % (self.street,self.city)

    def geocode(self, recode=False):
        """returns a tuple with lat and long for the adress
           If self.lat and self.long are not defined, the adress is
           geocoded. If they are defined, they are simply returned.
           If recode is True, geocoding is done in any case 
        """
        if not self.lat or not self.long or recode:
            # get the geocoordinates for the adress
            # TODO log geocodings into the db
            g = geocoders.Google(settings.GOOGLE_API_KEY)
            adr = '%s, %s %s, %s' % (self.street, self.zipcode, self.city, self.country)
            (self.lat, self.long) = g.geocode(adr)[1]
            self.save()
        return (self.lat, self.long)

     # TODO write a save function that assures that there is 
     # a geolocation or an city+country
    class Admin:
        pass


class Location(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(prepopulate_from=('name',))
   
    # contactdata  
    contactmail = models.EmailField(blank=True)
    # url = models.URLField(blank=True) 
    

    adress = models.ForeignKey('Adress', blank=True, null=True, unique=True) 
    icon = models.ImageField(blank=True, null=True, upload_to='/locations/') 

    # from the future: 
    #webresources = models.ManyToManyField(Webresource)

    class Admin:
        list_display = ('name',)
        search_fields = ('name',) 
        fields = (
          (None, {'fields': ('name','slug')}),
          (None, {'fields': ('adress','contactmail', 'icon')}),
#          ('Webinfo', {'fields': ('webresources',)}),
        )

    def save(self):
        """Saves the Location and takes care that there is a slug"""
        if not self.slug:
           self.slug = slugify(self.name) 
        super(Location, self).save()

    def __str__(self):
        return self.name

