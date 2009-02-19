__author__ = "Kirsten Jones <synedra@gmail.com>"
__version__ = "$Rev$"
__date_ = "$Date$"

import sys

import re
import oauth.oauth as oauth
import httplib
import time
from xml.dom.minidom import parseString
import simplejson

HOST 			  = 'api.netflix.com'
PORT              = '80'
REQUEST_TOKEN_URL = 'http://api.netflix.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'http://api.netflix.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api-user.netflix.com/oauth/login'

class NetflixError(Exception): pass

class NetflixUser():
	def __init__(self, user, client):
		self.request_token_url = REQUEST_TOKEN_URL
		self.access_token_url  = ACCESS_TOKEN_URL
		self.authorization_url = AUTHORIZATION_URL
		self.access_token = oauth.OAuthToken( user['access']['key'], user['access']['secret'] )
		self.client = client

	def getRequestToken(self):
		oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, http_url=self.request_token_url)
		oauth_request.sign_request(self.signature_method_hmac_sha1, self.consumer, None)
		client.connection.request(oauth_request.http_method, self.request_token_url, headers=oauth_request.to_header())
		response = client.connection.getresponse()
		request_token = oauth.OAuthToken.from_string(response.read())

		params = {'application_name': self.CONSUMER_NAME, 'oauth_consumer_key': self.CONSUMER_KEY}

		oauth_request = oauth.OAuthRequest.from_token_and_callback(token=request_token, callback=self.CONSUMER_CALLBACK,
		      http_url=self.authorization_url, parameters=params)

		return ( request_token, oauth_request.to_url() )

	
	def getAccessToken(self, request_token):
		if not isinstance(request_token, oauth.OAuthToken):
		        request_token = oauth.OAuthToken( request_token['key'], request_token['secret'] )
		oauth_request = oauth.OAuthRequest.from_consumer_and_token(	self.consumer,
									token=request_token,
									http_url=self.access_token_url)
		oauth_request.sign_request(	self.signature_method_hmac_sha1,
		self.consumer,
		request_token)
		self.connection.request(	oauth_request.http_method,
		self.access_token_url,
		headers=oauth_request.to_header())
		response = self.connection.getresponse()
		access_token = oauth.OAuthToken.from_string(response.read())
		return access_token
 	
 	## gets ratings for a list of titles
	## must provide the user's access token and either:
	##   disc_info - list of dicts from get_disc_info
	##   urls      - list of netflix id urls
	def getRatings(self, disc_info=[], urls=[]):
		access_token=self.access_token
		
		if not isinstance(access_token, oauth.OAuthToken):
			access_token = oauth.OAuthToken( access_token['key'], access_token['secret'] )
		
		request_url = '/users/%s/ratings/title' % (access_token.key)
		if not urls:
		           for disc in disc_info:
		                   urls.append( disc['id'] )
		parameters = { 'title_refs': ','.join(urls) }
		
		doc = parseString( self.client._get_resource( request_url, parameters=parameters, token=access_token ) )
		
		ret = {}
		for title in doc.documentElement.getElementsByTagName('ratings_item'):
		        links = title.getElementsByTagName('link')
		        discid = ''
		        for link in links:
		                if link.getAttribute('rel')=='http://schemas.netflix.com/id':
		                        discid = link.getAttribute('href')
		        
		        id2 = title.getElementsByTagName('id')[0].childNodes[0].data
		        ratings = {
		                'average': title.getElementsByTagName('average_rating')[0].childNodes[0].data,
		                'predicted': title.getElementsByTagName('predicted_rating')[0].childNodes[0].data,
		        }
		        try:
		                ratings['user'] = title.getElementsByTagName('user_rating')[0].childNodes[0].data
		        except:
		                noop=1
		        
		        if id2 in urls:
		                ret[ id2 ] = ratings
		        else:
		                ret[ discid ] = ratings
		
		return ret

		
 	
 	## add discs to the users disc queue
	## must provide the user's access token and either:
	##   disc_info - list of dicts from get_disc_info
	##   urls      - list of netflix id urls
	def queueDiscs(self, disc_info=[], urls=[]):
			access_token=self.access_token
			print access_token
			
			if not isinstance(access_token, oauth.OAuthToken):
				access_token = oauth.OAuthToken( access_token['key'], access_token['secret'] )
			
			request_url = '/users/%s/queues/disc' % (access_token.key)
			if not urls:
				for disc in disc_info:
					urls.append( disc['id'] )
			parameters = { 'title_ref': ','.join(urls) }
			
			response = self.client._get_resource( request_url, token=access_token )
			tag = re.search('<etag>(\d+)</etag>', response)
			parameters['etag'] = tag.group(1)
			print "THIS IS THE REQUEST"
			print request_url
			print access_token
			print parameters
			print "THAT WAS THE REQUEST"
			response = self.client._post_resource( request_url, token=access_token, parameters=parameters )
			return response

class NetflixCatalog():
	def __init__(self,client):
		self.client = client
	
	def searchMovieTitles(self, term):
	   request_url = '/catalog/titles'
	   parameters = {'term': term}
	   
	   doc = parseString( self.client._get_resource( request_url, parameters=parameters ) )
	   
	   best_result = doc.documentElement.getElementsByTagName('catalog_title')[0]
	   info = {}
	   info['title'] = best_result.getElementsByTagName('title')[0].getAttribute('regular')
	   box_art = best_result.getElementsByTagName('box_art')[0]
	   info['box_art'] = {
	           'small': box_art.getAttribute('small'),
	           'medium': box_art.getAttribute('medium'),
	           'large': box_art.getAttribute('large')
	   }
	   info['release_year'] = best_result.getElementsByTagName('release_year')[0].childNodes[0].data
	   info['average_rating'] = best_result.getElementsByTagName('average_rating')[0].childNodes[0].data
	   info['genres']=[]
	   info['links']={}
	   for category in best_result.getElementsByTagName('category'):
	           if category.getAttribute('scheme')=='http://api.netflix.com/categories/genres':
	                   info['genres'].append( category.getAttribute('label') )
	           if category.getAttribute('scheme')=='http://api.netflix.com/catalog/titles/mpaa_ratings':
	                   info['rating'] = category.getAttribute('label')
	   
	   for link in best_result.getElementsByTagName('link'):
	           if link.getAttribute('rel')=='http://schemas.netflix.com/id':
					info['id'] = link.getAttribute('href')
	           else:
	           		info['links'][ link.getAttribute('title') ] = link.getAttribute('href')
	   
	   if not id in info:
	           info['id'] = best_result.getElementsByTagName('id')[0].childNodes[0].data
	   
	   return info
		

class NetflixDisc:
	def __init__(self,disc_info,client):
		self.info = disc_info
		self.client = client
	
	## gets the available formats for a given title
	## provide either:
	##   disc_info - the dict from get_disc_info
	##   url       - the netflix id url
	def getAvailableFormats(self, url=None):
		if not url:
			url = self.info['links']['formats']
		
		doc = parseString( self.client._get_resource( url ) )
		
		formats = []
		for category in doc.documentElement.getElementsByTagName('category'):
			if category.getAttribute('scheme')=='http://api.netflix.com/categories/title_formats':
			     formats.append( category.getAttribute('label') )
		return formats
		


class NetflixClient:
	def __init__(self, name, key, secret, callback='',verbose=False):
		self.connection = httplib.HTTPConnection("%s:%s" % (HOST, PORT))
		self.server = HOST
		self.verbose = verbose
		self.user = None
		self.catalog = NetflixCatalog(self)

		
		self.CONSUMER_NAME=name
		self.CONSUMER_KEY=key
		self.CONSUMER_SECRET=secret
		self.CONSUMER_CALLBACK=callback
		self.consumer = oauth.OAuthConsumer(self.CONSUMER_KEY, self.CONSUMER_SECRET)
		self.signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
	
	def _get_resource(self, url, token=None, parameters=None):
		url = "http://%s%s" % (HOST, url)
		oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
								http_url=url,
								parameters=parameters,
								token=token)
		oauth_request.sign_request(	self.signature_method_hmac_sha1,
		self.consumer,
		token)
		if (self.verbose):
		        print oauth_request.to_url()
		self.connection.request('GET', oauth_request.to_url())
		response = self.connection.getresponse()
		return response.read()
	
	def _post_resource(self, url, token=None, parameters=None):
		url = "http://%s%s" % (HOST, url)
		oauth_request = oauth.OAuthRequest.from_consumer_and_token(	self.consumer,
								http_url=url,
								parameters=parameters,
								token=token,
								http_method='POST')
		oauth_request.sign_request(self.signature_method_hmac_sha1, self.consumer, token)
		
		headers = {'Content-Type' :'application/x-www-form-urlencoded'}
		self.connection.request('POST', url, body=oauth_request.to_postdata(), headers=headers)
		response = self.connection.getresponse()
		return response.read()


#######################################################
# example: netflix.py "The Professional" "Dark City"
#    add to queue: netflix.py -q "The Professional"

if __name__=="__main__":
		import getopt
		try:
		        opts, args = getopt.getopt(sys.argv[1:], "qva")
		except getopt.GetoptError, err:
		        # print help information and exit:
		        print str(err) # will print something like "option -a not recognized"
		        sys.exit(2)
		
		queuedisc=False
		verbose = False
		usertoken = False
		for o, a in opts:
				if o == "-v":
					verbose = True
				if o == "-q":
					queuedisc = True
				if o == '-a':
					usertoken = True
		
		APP_NAME   = 'Movie browser'
		API_KEY    = 'nbf4kr594esg4af25qexwtnu'
		API_SECRET = 'SSSeTdsPsM'
		CALLBACK   = 'http://www.synedra.org'
		
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
		
		netflix = NetflixClient(APP_NAME, API_KEY, API_SECRET,CALLBACK,verbose)
		if usertoken:
			netflix.user = NetflixUser(EXAMPLE_USER,netflix)
			
			if EXAMPLE_USER['request']['key'] and not EXAMPLE_USER['access']['key']:
			  tok = netflix.user.getAccessToken( EXAMPLE_USER['request'] )
			  print "now put this key / secret in EXAMPLE_USER.access so you don't have to re-authorize again:\n 'key': '%s',\n 'secret': '%s'\n" % (tok.key, tok.secret)
			  EXAMPLE_USER['access']['key'] = tok.key
			  EXAMPLE_USER['access']['secret'] = tok.secret
			  sys.exit(1)
			
			elif not EXAMPLE_USER['access']['key']:
			  (tok, url) = netflix.user.getRequestToken()
			  print "Authorize user access here: %s" % url
			  print "and then put this key / secret in EXAMPLE_USER.request:\n 'key': '%s',\n 'secret': '%s'\n" % (tok.key, tok.secret)
			  print "and run again."
			  sys.exit(1)

		
		discs=[]
		for arg in args:
		  data = netflix.catalog.searchMovieTitles(arg)
		  for info in data:
		        print "%s = %s" % (info, data[info])
		  disc = NetflixDisc(data,netflix)
		  formats = disc.getAvailableFormats()
		  print "formats = %s" % (formats)
		  if queuedisc:
				if not usertoken:
					print "Unable to add to queue without authorization (using -a)"
				else:
					print netflix.user.queueDiscs( urls=[data['id']])
		  discs.append( data )
		if usertoken and discs:
			ratings =  netflix.user.getRatings( discs )
			print "ratings = %s" % (ratings)