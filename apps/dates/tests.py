import unittest
from datetime import datetime, timedelta, time

from plotter.apps.dates.models import Date, Location, Adress
from plotter import settings

class DateManagerTestCase(unittest.TestCase):
    def setUp(self): 
        # create events for every day in one week
        g9 = Location.objects.create(name='Geb9')    
        g9.adress = Adress.objects.create(street='Deutz-Muelheimer',city='Koeln', country='de',zipcode='50111') 
        g9.save()
        rox = Location.objects.create(name='Roxy')    
        rox.adress = Adress.objects.create(country='de', zipcode='53117') 
        rox.save()
        days = 'Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday'.split(',')
        dayone = datetime(2009,9,15)  
        dates=[]
        # set up is getting called for every testcase. so i clear the table.
        Date.objects.all().delete() 
        for (i,day) in enumerate(days):
            dates.append( Date.objects.create(
               startdate = dayone+timedelta(days=i),   
               enddate = dayone+timedelta(days=i, minutes=90), 
               summary = day, 
               location = (i%2==0) and g9 or rox))

    def test_oneday(self):      
        # on 2009-9-19 the database should have 1 date
        dates = Date.objects.oneday(datetime(2009,9,19)) 
        out = ['oneday failed, dates on 2009-9-19: '] 
        for d in dates:
            out.append( '%s %s'% (str(d.startdate), d.summary) )
       
        self.assertEquals(len(dates),1, ' '.join(out) ) 

    def test_bydate(self):      
        dates = Date.objects.by_date('2009-09')
        self.assertEquals(len(dates),7) 
       
        dates = Date.objects.by_date('2009-09-15')
        self.assertEquals(len(dates),1) 
        self.assertEquals(dates[0].summary,'Monday') 
        self.assertEquals(dates[0].slug,'monday') 

        # TODO write tests for tommorrow 
         
    def test_byplace(self):
        # test if the selection by place works 
        dates = Date.objects.by_place('de-53117')         
        #dates = Date.objects.published() 
        out = []
        for d in dates:
            out.append( '%s %s'% (str(d.startdate), d.location.adress.country) )
        self.assertEquals(len(dates),3,'|'.join(out)) 

#    def test_chainging(self):
#        dates = Date.objects.by_date('2009-09').by_place('de-50')
#        self.assertEquals(len(dates),4) 


    def test_bydateandplace(self):      
        dates = Date.objects.by_date_and_place('2009-09', 'de', '50')
        self.failUnless(len(dates)>2, 'len(dates)==%s' % str(len(dates)) )
        self.failUnless(len(dates)<5)
         
        dates = Date.objects.by_date_and_place('2009-09', 'de', '53117')
        self.failUnless(len(dates)>2)
        self.failUnless(len(dates)<5)

class DateTestCase(unittest.TestCase):
    def test_duration(self):      
        rox = Location.objects.create(name='Roxy')    
        rox.adress = Adress.objects.create(country='de', zipcode='53117') 
        day = datetime(2008, 5, 13, 20, 30) 
        d = Date.objects.create(
            startdate = day,   
            enddate = day+timedelta(minutes=90), 
            summary = 'Domingo Club', 
            location = rox) 
        self.assertEquals(d.slug, 'domingo-club', 'Slug of date incorrect.') 
        self.assertEquals(d.duration().seconds/60, 90, 'Duration of date is incorrect.') 

    def test_startdatetime(self):      
        """There are separate fields for startdate and time. 
           the method startdatetime() returns a datetime object combine startdate and time.""" 
        rox = Location.objects.create(name='Roxy')    
        rox.adress = Adress.objects.create(country='de', zipcode='53117') 
        day = datetime(2008, 5, 13, 20, 30) 
        d = Date.objects.create(
            startdate = day,   
            starttime = time(20,30), 
            enddate = day+timedelta(minutes=90), 
            summary = 'Domingo Club', 
            location = rox) 
        self.assertEquals( str(d.startdatetime()), '2008-05-13 20:30:00' ) 

    def test_adress(self):
        """The Adress of an event should always be accessable via date.adress, even if its the adress of the location."""   
        day = datetime(2008, 5, 13, 20, 30) 
        a = Adress.objects.create(street='Sesame',city='koeln',country='de')
        d = Date.objects.create(
            startdate = day,   
            starttime = time(20,30), 
            enddate = day+timedelta(minutes=90), 
            summary = 'Sesame Club',
            adress = a
            ) 
        self.assertEquals(d.adress.street, 'Sesame')
        a2 = Adress.objects.create(street='Poppy',city='koeln',country='de')
        rox = Location.objects.create(name='Roxy',adress=a2)    
        d.location = rox
        d.save()
        self.assertEquals(d.adress.street, 'Poppy')
       
        # TODO:  test is not finished.  
        # test removing a location. 

    def test_static_map(self): 
        """Test the function get_get_static_map"""
        # create a date with adress
        day = datetime(2008, 5, 13, 20, 30) 
        a = Adress.objects.create(street='Breitestrasse',city='Koeln',country='de')
        d = Date.objects.create(
            startdate = day,   
            starttime = time(20,30), 
            enddate = day+timedelta(minutes=90), 
            summary = 'Sesame Club',
            adress = a
            ) 

        # this test will break if google changes the url
        self.failUnless( d.get_static_map().startswith('http://maps.google.com/staticmap') )  


        # create a date without adress
        day = datetime(2008, 5, 13, 20, 30) 
        d = Date.objects.create(
            startdate = day,   
            starttime = time(20,30), 
            enddate = day+timedelta(minutes=90), 
            summary = 'Sesame Club',
            ) 

        self.assertEquals(d.get_static_map(), settings.NO_STATIC_MAP) 
       
        #TODO: test behaviour for a date with a location with an adress

        
        

class LocationTestCase(unittest.TestCase):
    def test_creation(self): 
        g9 = Location.objects.create(name='Geb9')    
        g9.save() 
        self.assertEquals(g9.slug, 'geb9','Slug of Location incorrect.') 
        

class AdressTestCase(unittest.TestCase):
    def setUp(self):
        self.g9a = Adress.objects.create( 
          street = 'Deutz-Muelheimer-Strasse 127-129',
          city = 'koeln', 
          country = 'de',
        )  
          
    def test_creation(self):      
        g9a = Adress.objects.create( 
          street = 'Deutz-Muelheimer-Strasse 127-129',
          city = 'koeln', 
          country = 'de',
        )  
        
        g9a.save() 

        geoonly= Adress.objects.create( 
          lat='50',
          long='60' 
        )  
        geoonly.save() 

    def test_geocode(self):
        (lat, long) = self.g9a.geocode()            
        self.failUnless(str(lat).startswith('50.94'),'Latitude not correct geocoded.')
        self.failUnless(str(long).startswith('6.98'),'Longitude not correct geocoded.')

    def test_recode(self):
        self.g9a.lat = '48.8581'
        self.g9a.long = '2.2945' 
        (lat, long) = self.g9a.geocode()            
        self.failUnless(str(lat).startswith('48.85'))
        self.failUnless(str(long).startswith('2.29'))

        (lat, long) = self.g9a.geocode(True)            
        self.failUnless(
            str(lat).startswith('50.94') and str(long).startswith('6.98'),
            'Geocode not correctly overwritten. Lat should be 50.94 and is %s' % str(lat))



class OrganizerTestCase(unittest.TestCase):
    pass



