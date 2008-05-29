from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from datetime import datetime, timedelta

from plotter import settings
from plotter.utils import static_map
from plotter.apps.dates.managers import DateManager

from plotter.apps.locations.models import Adress, Location


#TODO:  this should go to the database to avoid having to 
# deploy new code for changing categories
DATE_CATEGORIES = (
  ( 'party'    , 'Party'),
  ( 'concert'  , 'Concert'),
  ( 'cinema'   , 'Cinema') ,
  ( 'theater'  , 'Theater'),
  ( 'food'     , 'Food'),
  ( 'sports'   ,  'Sports'),
  ( 'art'      , 'Art'),
)

class Organizer(models.Model): 
    name = models.CharField(max_length=100)
    slug = models.SlugField(prepopulate_from=('name', ))

#    description = models.TextField(blank=True)

    # contact data 
#    phone = models.CharField(max_length=30, blank=True) 
#    email = models.EmailField(blank=True);
#    web = models.URLField(blank=True); 

    #webresources = models.ManyToManyField(Webresource)
    
    def __str__(self):
        return self.name

    class Admin:
        pass


class Date(models.Model):
    """Represents one Date in the Calendar"""
    slug = models.SlugField(prepopulate_from=('summary',), unique_for_date='startdate')
   
    # ical-related fields
    startdate    = models.DateField()
    starttime    = models.TimeField(blank=True, null=True)
    enddate      = models.DateTimeField() 
    summary      = models.CharField(unique_for_date='startdate', max_length=250)
    description  = models.TextField(blank=True)
    organizer    = models.ForeignKey(Organizer, blank=True, null=True) 
    location     = models.ForeignKey(Location, blank=True, null=True) 
    adress       = models.ForeignKey(Adress, blank=True, null=True) 

    category = models.CharField(max_length=100, default='party', choices=DATE_CATEGORIES)
   
    # technical fields
    owner = models.ForeignKey(User, blank=True, null=True)
    created = models.DateTimeField(auto_now=True) 
    modified = models.DateTimeField(auto_now_add=True) 

    publish = models.BooleanField(default=True)

    #community-related-fields 
    #inapropriate = models.ManyToManyField(User)
    #spam         = many2many
    #attending    = many2many
    #permissions  = permission
    
    allowcomments = models.BooleanField(default=True)

# future releases:
    # date can belong to a regular. 
#    regular      = models.ForeignKey(Regular) 
    # indicator if the date is deviated from its rule
#    offbeat      = models.BooleanField(default=False)  

#    webresources = models.ManyToManyField(Webresource)

    # Dates have a custom manager...
    objects = DateManager() 

    def has_map(self): 
        """Returns True if date has an adress""" 
        # check for an adress
        if not self.adress:
            if self.location: # if there's no adress, but a location
                self.save()   # saving fills the  adress
            else:
                return False

        if not self.adress: 
            return False
 
        # try to geocode the adress if no lat/long-pair is there. 
        if (not self.adress.lat) or (not self.adress.long):
            self.adress.geocode() 

        if (not self.adress.lat) or (not self.adress.long):
            return False

        return True 
 
    def get_static_map(self): 
        """Returns a url to a picture with a map showing the location of the date."""
        if not self.has_map():
            return settings.NO_STATIC_MAP # returns url to a standart picture.

        params = { 
           'lat': self.adress.lat, 
           'long': self.adress.long, 
           'markers': [ { 'lat': self.adress.lat, 'long':self.adress.long  } ],
        } 
        return static_map(params)

    def __str__(self):
        return '%s - %s' % (self.startdate.strftime('%d.%m.%Y'), self.summary) 

    # should be removed
    def _get_absolute_url(self):
        "returns the unique url to this date"
        return ('single_by_id', (), {
           'year': self.startdate.year,
           'month': self.startdate.month,
           'day': self.startdate.day,
           'slug': self.slug})
    _get_absolute_url = models.permalink(_get_absolute_url)

    def get_absolute_url(self):
        "returns the unique url to this date"
        return ('single_by_id', (), {
           'id': self.id })
    get_absolute_url = models.permalink(get_absolute_url)


    def startdatetime(self): 
        "Returns a datetime object for the start-date and time of the date" 
        return datetime.combine(self.startdate, self.starttime) 

    def de_normalize(self):
        """to deliver more information on a single request,
           de-normalize the object. 
           mainly for use with json."""
        # TODO: check if de-normalization is somehow saved by
        # self.save()  that would be bad.
        
        #self.adressdata = self.adress     
        # the adress is denormalized directly to the date object
        # because at the time writing TaffyDB doesn't support querying
        # on sub-objects. 
        self.city = self.adress.city
        self.zipcode = self.adress.zipcode
        self.street = self.adress.street
        self.country = self.adress.country
        self.lat = self.adress.lat
        self.long = self.adress.long

        self.locationdata = self.location   
        self.absolute_url = self.get_absolute_url() 
        self.start_datetime = self.startdatetime()

    def as_json(self):
        """returns a json-representation of the date"""
        # changes to the json output should be documented in:
        # http://code.google.com/p/plottr/wiki/JsonModels
        from plotter.utils import json_encode
        # the joined models are de-normalized into the the date-model
        # in order to cut down on ajax requests.
        self.de_normalize(); 
        json = json_encode(self) 
        return json

    #TODO
    def as_ical(self):
        """returns an ical-string-representation of the date"""
        return 'ical'

    def save(self):
        """Saves the Location and takes care that there is a slug"""

        # if the date has an adress the adress is redundantly saved in the
        # date-model in oder to allow easy querying. 
        if self.location and self.location.adress:
            self.adress = self.location.adress

        if not self.slug:
           self.slug = slugify(self.summary) 
        super(Date, self).save()

    def duration(self):
        return self.enddate-self.startdate
 

    # should there be special fields for musical events like 'performer'?
    # sould there be a field for a entry-fee?
    class Meta:
        get_latest_by = 'startdate'
        ordering = ['startdate', 'starttime', 'location', 'slug']
 
    class Admin: 
        list_display = ('slug', 'startdate', 'summary', 'publish')
        list_filter = ('startdate', 'publish')
        search_fields = ('slug', 'summary', 'description') 
        date_hierarchy = 'startdate'
        fields = (
          (None, {'fields': ('startdate','starttime','enddate','summary','slug',)}),
          (None, {'fields': ('description', 'organizer', 'location', 'adress')}),
          (None, {'fields': ('publish', 'category', 'allowcomments')}),
          #('Webinfo', {'fields': ('webresources',)}),
        )
         

