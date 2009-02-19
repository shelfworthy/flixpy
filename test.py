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

class TestQuery():
	def test_base(self):
		netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK)
		
	def test_searchMovieTitles(self):
		netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK)
		data = netflixClient.catalog.searchMovieTitles(MOVIE_TITLE)
		for info in data['catalog_titles']['catalog_title']:
			assert isinstance(info['title']['regular'],unicode)

	def test_searchStringMovieTitles(self):
		netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK)
		data = netflixClient.catalog.searchStringMovieTitles('Foo')
		for info in data['autocomplete']['autocomplete_item']:
			assert re.search('Foo',info['title']['short'])
			
	# DISC TESTS
	def test_disc_functions(self):
		netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK)
		data = netflixClient.catalog.searchMovieTitles(MOVIE_TITLE)
		testSubject = data['catalog_titles']['catalog_title'][10]
		disc = NetflixDisc(testSubject,netflixClient)
		formats = disc.getAvailableFormats()
		assert isinstance(formats,dict)
		synopsis = disc.getSynopsis()
		assert isinstance(synopsis,dict)
				
	def test_user_functions(self):
		netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK)
		netflixUser = NetflixUser(EXAMPLE_USER,netflixClient)
		data = netflixClient.catalog.searchMovieTitles(MOVIE_TITLE)
		discs = data['catalog_titles']['catalog_title']
		ratings = netflixUser.getRatings(discs)

if __name__ == '__main__':
    unittest.main() 
