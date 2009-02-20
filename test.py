# Sample code to use the Netflix python client
import unittest, os
import simplejson
from Netflix import *

APP_NAME   = ''
API_KEY    = ''
API_SECRET = ''
CALLBACK   = ''

MOVIE_TITLE = "Foo Fighters"

EXAMPLE_USER = {
        'request': {
                'key': '',
                'secret': ''
        },
        'access': {
                'key': '',
                'secret': ''
        }
}

EMPTY_USER = {
        'request': {
                'key': '',
                'secret': ''
        },
        'access': {
                'key': '',
                'secret': ''
        }
}

class TestQuery():
	def test_base(self):
		netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK)
		
	def test_token_functions(self):
		netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK)
		netflixUser = NetflixUser(EMPTY_USER,netflixClient)
		# I'd love to test the token functions, but unfortunately running these
		# invalidates the existing tokens.  Foo.

		
	def test_catalog_functions(self):
		netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK)
		data = netflixClient.catalog.searchStringTitles('Foo')
		for info in data:
			assert re.search('Foo',info['title']['short'])
			
		data = netflixClient.catalog.searchTitles(MOVIE_TITLE)
		assert isinstance(data[0]['title']['regular'],unicode)
		
		movie = netflixClient.catalog.getTitle(data[0]['id'])
		assert isinstance(movie['catalog_title']['title']['regular'],unicode)
		
		people = netflixClient.catalog.searchPeople('Flip Wilson',maxResults=1)
		assert isinstance(people,dict)
		
	# DISC TESTS
	def test_disc_functions(self):
		netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK)
		data = netflixClient.catalog.searchTitles(MOVIE_TITLE)
		testSubject = data[10]
		disc = NetflixDisc(testSubject,netflixClient)
		formats = disc.getInfo('formats')
		assert isinstance(formats,dict)
		synopsis = disc.getInfo('synopsis')
		assert isinstance(synopsis,dict)	  
				
	def test_user_functions(self):
		netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK)
		netflixUser = NetflixUser(EXAMPLE_USER,netflixClient)
		user = netflixUser.getData()
		assert isinstance(user['first_name'],unicode)
		data = netflixClient.catalog.searchTitles(MOVIE_TITLE)
		ratings = netflixUser.getRatings(data)
		history = netflixUser.getRentalHistory('shipped',updatedMin=1219775019,maxResults=4)
		assert int(history['rental_history']['number_of_results']) <= 5

if __name__ == '__main__':
    unittest.main() 
