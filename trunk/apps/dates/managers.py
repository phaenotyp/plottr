from django.db import models
from datetime import datetime, timedelta

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


