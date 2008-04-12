from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from datetime import datetime, timedelta
from geopy import geocoders  

from plotter import settings


DATE_CATEGORIES = {
   'party'    : 'Party',
   'concert'  : 'Concert',
   'cinema'   : 'Cinema', 
   'theater'  : 'Theater',
   'food'     : 'Food',
   'political': 'Political',
   'sports'   : 'Sports',
   'art'      : 'Art',
}

COUNTRY_CHOICES = (
 ( 'de' , 'de'),
)

# TODO this has to go in its own file 

class DateManager(models.Manager):
    """A Custom Manager for Dates""" 
    def published(self):
        """Returns a queryset of all published dates"""
        return self.filter(publish=True) 

    def oneday(self, startdate): 
        """returns a queryset with all dates on the passed datetimes day"""
        return self.published().filter(
              startdate__year=startdate.year,
              startdate__month=startdate.month,
              startdate__day=startdate.day
                                      ) 

    def today(self): 
        """returns a queryset of all published dates today"""
        return self.oneday(datetime.datetime.today()) 

    def by_place( self, place ):  
        (country, zipcode) = place.split('-')  
        return self.published().filter(adress__country__iexact=country, adress__zipcode__istartswith=zipcode)

    def by_date_and_place(self, date, place):
        (country, zipcode) = place.split('-')  
        return self.by_date(date).filter(adress__country__iexact=country, adress__zipcode__istartswith=zipcode) 
        

    def by_date(self, date):
        """Returns a queryset of dates matching a date"""
         
        # TODO handle the case if date is a datetime-object

        # first try if date matches a set of strings 
        if date.lower() == 'all': # all dates
            return self.published()
        if date.lower() == 'today': # dates for today 
            return self.today()
        if date.lower() == 'tomorrow':  # date for manana
            return self.oneday(datetime.today()+timedelta(days=+1))

        # second try if date is a minus(-)-seperated date
        qs = self.published() 
        parts = date.split('-') 
        if len(parts)>=1: # dates for a certain year
            qs = qs.filter(startdate__year=int(parts[0])) 
           
        if len(parts)>=2: # dates for a certain year and month
            qs = qs.filter(startdate__month=int(parts[1])) 
           
        if len(parts)==3: # dates for a certain day
            qs = qs.filter(startdate__day=int(parts[2])) 
        return qs

        # not a match
        #  TODO log the value of date, for future optimization and
        #  TODO return an empty queryset, i guess 
 
class Organizer(models.Model): 
    name = models.CharField(max_length=100)
    slug = models.SlugField(prepopulate_from=('name', ))
     

    #webresources = models.ManyToManyField(Webresource)
    
    def __str__(self):
        return self.name

    class Admin:
        pass


class Adress(models.Model): 
    """Represents one Adress""" 
    street  = models.CharField(max_length=100, blank=True)
    city    = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, choices=COUNTRY_CHOICES)
    zipcode = models.CharField(max_length=20, blank=True)
    lat     = models.FloatField(blank=True, null=True)
    long    = models.FloatField(blank=True, null=True)

    #location = models.ForeignKey('Location', edit_inline=models.STACKED, num_in_admin=1, blank=True, null=True, unique=True) # should be one-to-one 

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
            g = geocoders.Google(settings.google_api_key)
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
    
    contactmail = models.EmailField(blank=True)
    
    adress = models.ForeignKey('Adress', blank=True, null=True, unique=True) # should be one-to-one 
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

    def __str__(self):
        return '%s - %s' % (self.startdate.strftime('%d.%m.%Y'), self.summary) 

    def get_absolute_url(self):
        return ('single', (), {
           'year': self.startdate.year,
           'month': self.startdate.month,
           'day': self.startdate.day,
           'slug': self.slug})
    get_absolute_url = models.permalink(get_absolute_url)

    def startdatetime(self): 
        return datetime.combine(self.startdate, self.starttime) 

    #TODO
    def as_json(self):
        """returns a json-representation of the date"""
        return '{}'

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
    # should there be a field 
    class Meta:
        get_latest_by = 'startdate'
        ordering = ['startdate', 'starttime', 'location', 'slug']
 
    class Admin: 
        list_display = ('slug', 'startdate', 'summary', 'publish')
        list_filter = ('startdate', 'publish')
        search_fields = ('slug', 'summary', 'description') 
        date_hierarchy = 'startdate'
        fields = (
          (None, {'fields': ('startdate','starttime','enddate','summary','slug')}),
          (None, {'fields': ('description', 'organizer', 'location')}),
          (None, {'fields': ('publish', 'allowcomments')}),
          #('Webinfo', {'fields': ('webresources',)}),
        )
         

