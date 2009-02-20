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
		self.data = None

	def getRequestToken(self):
		client = self.client
		oauth_request = oauth.OAuthRequest.from_consumer_and_token(client.consumer, http_url=self.request_token_url)
		oauth_request.sign_request(client.signature_method_hmac_sha1, client.consumer, None)
		client.connection.request(oauth_request.http_method, self.request_token_url, headers=oauth_request.to_header())
		response = client.connection.getresponse()
		request_token = oauth.OAuthToken.from_string(response.read())

		params = {'application_name': client.CONSUMER_NAME, 'oauth_consumer_key': client.CONSUMER_KEY}

		oauth_request = oauth.OAuthRequest.from_token_and_callback(token=request_token, callback=client.CONSUMER_CALLBACK,
		      http_url=self.authorization_url, parameters=params)

		return ( request_token, oauth_request.to_url() )

	
	def getAccessToken(self, request_token):
		client = self.client
		
		if not isinstance(request_token, oauth.OAuthToken):
		        request_token = oauth.OAuthToken( request_token['key'], request_token['secret'] )
		oauth_request = oauth.OAuthRequest.from_consumer_and_token(	client.consumer,
									token=request_token,
									http_url=self.access_token_url)
		oauth_request.sign_request(	client.signature_method_hmac_sha1,
									client.consumer,
									request_token)
		client.connection.request(	oauth_request.http_method,
									self.access_token_url,
									headers=oauth_request.to_header())
		response = client.connection.getresponse()
		access_token = oauth.OAuthToken.from_string(response.read())
		return access_token
 	
	def getData(self):
		access_token=self.access_token

		if not isinstance(access_token, oauth.OAuthToken):
			access_token = oauth.OAuthToken( access_token['key'], access_token['secret'] )
		
		request_url = '/users/%s' % (access_token.key)
		
		info = simplejson.loads( self.client._get_resource( request_url, token=access_token ) )
		self.data = info['user']
		return self.data
		
	def getInfo(self,field):
		access_token=self.access_token
		
		if not self.data:
			self.getData()
			
		fields = []
		url = ''
		for link in self.data['link']:
				fields.append(link['title'])
				if link['title'] == field:
					url = link['href']
					
		if not url:
			errorString = "Invalid or missing field.  Acceptable fields for this object are:\n" + "\n".join(fields)
			raise Exception(errorString)		
		try:
			info = simplejson.loads(self.client._get_resource( url,token=access_token ))
		except :
			return []
		else:
			return info
		
 	def getRatings(self, disc_info=[], urls=[]):
		access_token=self.access_token
		
		if not isinstance(access_token, oauth.OAuthToken):
			access_token = oauth.OAuthToken( access_token['key'], access_token['secret'] )
		
		request_url = '/users/%s/ratings/title' % (access_token.key)
		if not urls:
		           for disc in disc_info:
						urls.append(disc['id'])
		parameters = { 'title_refs': ','.join(urls) }
		
		info = simplejson.loads( self.client._get_resource( request_url, parameters=parameters, token=access_token ) )
		
		ret = {}
		for title in info['ratings']['ratings_item']:
				ratings = {
		                'average': title['average_rating'],
		                'predicted': title['predicted_rating'],
		        }
				try:
					ratings['user'] = title['user_rating']
				except:
					pass
		        
				ret[ title['title']['regular'] ] = ratings
		
		return ret

	def queueDiscs(self, disc_info=[], urls=[]):
		access_token=self.access_token
		
		if not isinstance(access_token, oauth.OAuthToken):
			access_token = oauth.OAuthToken( access_token['key'], access_token['secret'] )
		
		request_url = '/users/%s/queues/disc' % (access_token.key)
		if not urls:
			for disc in disc_info:
				urls.append( disc['id'] )
		parameters = { 'title_ref': ','.join(urls) }
		
		response = simplejson.loads(self.client._get_resource( request_url, token=access_token ))
		tag = response["queue"]["etag"]
		response = self.client._post_resource( request_url, token=access_token, parameters=parameters )
		print response
		return response

class NetflixCatalog():
	def __init__(self,client):
		self.client = client
	
	def searchTitles(self, term,startIndex=None,maxResults=None):
	   request_url = '/catalog/titles'
	   parameters = {'term': term}
	   if startIndex:
		   parameters['startIndex'] = startIndex
	   if maxResults:
		   parameters['maxResults'] = maxResults
	   info = simplejson.loads( self.client._get_resource( request_url, parameters=parameters))

	   return info['catalog_titles']['catalog_title']

	def searchStringTitles(self, term,startIndex=None,maxResults=None):
	   request_url = '/catalog/titles/autocomplete'
	   parameters = {'term': term}
	   if startIndex:
		   parameters['startIndex'] = startIndex
	   if maxResults:
		   parameters['maxResults'] = maxResults

	   info = simplejson.loads( self.client._get_resource( request_url, parameters=parameters))
	   print simplejson.dumps(info)
	   return info['autocomplete']['autocomplete_item']
	
	def getTitle(self, url):
	   request_url = url
	   info = simplejson.loads( self.client._get_resource( request_url ))
	   return info

	def searchPeople(self, term,startIndex=None,maxResults=None):
	   request_url = '/catalog/people'
	   parameters = {'term': term}
	   if startIndex:
		   parameters['startIndex'] = startIndex
	   if maxResults:
		   parameters['maxResults'] = maxResults

	   try:
	   	   info = simplejson.loads( self.client._get_resource( request_url, parameters=parameters))
	   except:
		   return []

	   return info['people']['person']

	def getPerson(self,url):
		request_url = url
		info = simplejson.loads( self.client._get_resource( request_url ))
		return info
		
		  

class NetflixDisc:
	def __init__(self,disc_info,client):
		self.info = disc_info
		self.client = client
	
	def getInfo(self,field):
		fields = []
		url = ''
		for link in self.info['link']:
				fields.append(link['title'])
				if link['title'] == field:
					url = link['href']
		if not url:
			errorString = "Invalid or missing field.  Acceptable fields for this object are:\n" + "\n".join(fields)
			raise Exception(errorString)		
		try:
			info = simplejson.loads(self.client._get_resource( url ))
		except :
			return []
		else:
			return info
			
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
	
	def _get_resource(self, url, token=None, parameters={}):
		if not re.match('http',url):
			url = "http://%s%s" % (HOST, url)
		parameters['output'] = 'json'
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