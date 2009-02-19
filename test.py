# Sample code to use the Netflix python client
import unittest, os
import simplejson
from Netflix import *

APP_NAME   = 'Movie browser'
API_KEY    = 'nbf4kr594esg4af25qexwtnu'
API_SECRET = 'SSSeTdsPsM'
CALLBACK   = 'http://www.synedra.org'

MOVIE_TITLE = "Foo Fighters"

EXAMPLE_USER = {
        'request': {
                'key': 'hwq8evzp4z2btfx5en9pfkvt',
                'secret': 'btrdgnyQcVxZ'
        },
        'access': {
                'key': 'T1lSMROEioV5Fio4RCWnRgSKe2pqg.W7pOgp8jBlf_Z5CUp0_9CtnXOpU.iVC4uw8U7qkD4BmEZIZfTyJcJWfe6Q--',
                'secret': 'RjQcVfVvyPnZ'
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
