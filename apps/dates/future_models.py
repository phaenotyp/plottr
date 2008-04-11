
# this file contains code or notes that are likely to end 
# in models.py in a future release. 

from django.db import models
from datetime import datetime, timedelta

RESOURCE_RELATIONS = {
   'home'        : 'Home',
   'alternate'   : 'Alternative Representation',
   'promo'       : 'Promotional',
   'doc'         : 'Documentational',
   'further'     : 'Further Information',
   'participant' : 'Participant',
}


class Regular(models.Model): 
    name = models.CharField(max_length=100) 
    rrule = models.TextField()   
    # a plain text description of the rule 
    # "Jeden Sonntag um 11.00 Uhr"  
    rule_description = models.CharField(max_length=200)  
 
    # new dates should be instatiated `createdelta` days before  
    # their occurance  
    createdelta       = models.IntegerField()  
    last_created_date = models.ForeignKey(Date)  
    
    # ical-related fields 
    first_date   = models.DateField() 
    starttime    = models.TimeField()  
    duration     = models.IntegerField(default=90)  # in minutes 
    summary      = models.CharField() 
    description  = models.TextField(blank=True) 
    organizer    = models.ForeignKey(Organizer)  
  
 
    webresources = models.ManyToManyField(Webresource) 
   
    # technical fields 
    owner = models.ForeignKey(User) 
    created = models.DateTimeField(auto_now=True)  
    modified = models.DateTimeField(auto_now_add=True)  
 
 
    allowcomments = models.BooleanField(default=True) 
 
    def instantiate( self, startdate=null, enddate=null ): 
        if (not startdate) and self.last_created_date: 
            startdate = self.last_created_date.startdate  
        if not enddate: 
            enddate = startdate+datetime.timedelda(days=self.createddelta)   
         
             
 
        # log -> instatized n date for self name  


class Event(models.Model):
    """Represents a group of Dates"""
    name = models.CharField(max_length=100, unique_for_year='startdate')
    slug = models.SlugField(prepopulate_by='name', unique_for_year='startdate')
    #type = models.CharField(max_length=100)  ? 

    # time constraints of an event. 
    # if a user tries to associate a date with an event out of this timeframe,  
    # constraints could be updated or association could be forbidden.
    startdate    = models.DateTimeField(blank=True, null=True)
    enddate      = models.DateTimeField(blank=True, null=True)
    # defines if new dates can strech the date-boundaries of an event.
    constraining  = models.BooleanField(default=False, help_text="Sind Start- und Endzeitpunkt fix oder koennen sie durch neue Termine verschoben werden?")

    icon = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.slug + ' ' + str(self.startdate.year)

    class Admin:
        list_display = ('name', 'startdate')
        date_hierarchy = ('startdate')
        fields=(
          (None, {'fields': ('name', 'slug')}),
          (None, {'fields': ('startdate', 'enddate', 'contstraining')}),
        )



class Webresource(models.Model):
    """Defines a link to another website. Will be programmaticly fetched and parsed according to mimetype, content, whatever ..."""
    url = models.URLField()
    relation = models.CharField(choices=RESOURCE_RELATIONS)

    def html(self):
        """Gets the Page and parses meaningful... """
        pass

