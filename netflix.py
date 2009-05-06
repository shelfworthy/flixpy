import sys, os.path, re, httplib, time, urllib2, gzip, StringIO
import oauth.oauth as oauth
from xml.dom.minidom import parseString
from urlparse import urlparse
from datetime import datetime

try:
    import simplejson
except ImportError:
    from django.utils import simplejson

HOST              = 'api.netflix.com'
PORT              = '80'
REQUEST_TOKEN_URL = 'http://api.netflix.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'http://api.netflix.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api-user.netflix.com/oauth/login'


class NetflixError(Exception):
    pass


class NetflixUser():
    def __init__(self, user, client):
        self.requestTokenUrl = REQUEST_TOKEN_URL
        self.accessTokenUrl  = ACCESS_TOKEN_URL
        self.authorizationUrl = AUTHORIZATION_URL
        self.accessToken = oauth.OAuthToken( user['access']['key'],
                                             user['access']['secret'] )
        self.client = client
        self.data = None

    @property
    def name(self):
        first = self.getData()['first_name']
        last = self.getData()['last_name']

        return "%s %s" % (first, last)

    @property
    def preferred_formats(self):
        if isinstance(self.getData()['preferred_formats']['category'], list):
            formats = []
            for format in self.getData()['preferred_formats']['category']:
                formats.append(format['term'])
            return formats
        else:
            return [self.getData()['preferred_formats']['category']['term']]

    @property
    def can_instant_watch(self):
        return self.getData()['can_instant_watch'] == 'true'

    @property
    def at_home(self):
        if isinstance(self.getInfo('at home')['at_home']['at_home_item'], list):
            movies = []
            for raw_movie in self.getInfo('at home')['at_home']['at_home_item']:
                movies.append(NetflixDisc(raw_movie,self.client))
            return movies
        else:
            return [NetflixDisc(self.getInfo('at home')['at_home']['at_home_item'],self.client)]

    def getRequestToken(self):
        client = self.client
        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(
                                    client.consumer,
                                    http_url=self.requestTokenUrl)
        oauthRequest.sign_request(
                                    client.signature_method_hmac_sha1,
                                    client.consumer,
                                    None)
        client.connection.request(
                                    oauthRequest.http_method,
                                    self.requestTokenUrl,
                                    headers=oauthRequest.to_header())
        response = client.connection.getresponse()
        requestToken = oauth.OAuthToken.from_string(response.read())

        params = {'application_name': client.CONSUMER_NAME, 
                  'oauth_consumer_key': client.CONSUMER_KEY}

        oauthRequest = oauth.OAuthRequest.from_token_and_callback(
                                    token=requestToken,
                                    callback=client.CONSUMER_CALLBACK,
                                    http_url=self.authorizationUrl,
                                    parameters=params)

        return (requestToken, oauthRequest.to_url())
   
    def getAccessToken(self, requestToken):
        client = self.client
        
        if not isinstance(requestToken, oauth.OAuthToken):
                requestToken = oauth.OAuthToken(
                                    requestToken['key'],
                                    requestToken['secret'])
        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(
                                    client.consumer,
                                    token=requestToken,
                                    http_url=self.accessTokenUrl)
        oauthRequest.sign_request(  client.signature_method_hmac_sha1,
                                    client.consumer,
                                    requestToken)
        client.connection.request(  oauthRequest.http_method,
                                    self.accessTokenUrl,
                                    headers=oauthRequest.to_header())
        response = client.connection.getresponse()

        accessToken = oauth.OAuthToken.from_string(response.read())
        return accessToken
    
    def getData(self):
        accessToken=self.accessToken

        if not isinstance(accessToken, oauth.OAuthToken):
            accessToken = oauth.OAuthToken(
                                    accessToken['key'],
                                    accessToken['secret'])
        
        requestUrl = '/users/%s' % (accessToken.key)
        
        info = simplejson.loads( self.client._getResource(
                                    requestUrl,
                                    token=accessToken))
        self.data = info['user']
        return self.data
        
    def getInfo(self, field):
        accessToken=self.accessToken
        
        if not self.data:
            self.getData()
            
        fields = []
        url = ''
        for link in self.data['link']:
                fields.append(link['title'])
                if link['title'] == field:
                    url = link['href']
                    
        if not url:
            errorString =           "Invalid or missing field.  " + \
                                    "Acceptable fields for this object are:"+ \
                                    "\n\n".join(fields)
            print errorString
            sys.exit(1)
        try:
            info = simplejson.loads(self.client._getResource(
                                    url,token=accessToken ))
        except:
            return []
        else:
            return info
        
    def getRatings(self, discInfo=[], urls=[]):
        accessToken=self.accessToken
        
        if not isinstance(accessToken, oauth.OAuthToken):
            accessToken = oauth.OAuthToken( 
                                    accessToken['key'], 
                                    accessToken['secret'] )
        
        requestUrl = '/users/%s/ratings/title' % (accessToken.key)
        if not urls:
            if isinstance(discInfo,list):
                for disc in discInfo:
                    urls.append(disc['id'])
            else:
                urls.append(discInfo['id'])
        parameters = { 'title_refs': ','.join(urls) }
        
        info = simplejson.loads( self.client._getResource(
                                    requestUrl,
                                    parameters=parameters,
                                    token=accessToken ) )
        
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

    def getRentalHistory(self,type=None,startIndex=None,
                                    maxResults=None,updatedMin=None):
        accessToken=self.accessToken
        parameters = {}
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults
        if updatedMin:
            parameters['updated_min'] = updatedMin

        if not isinstance(accessToken, oauth.OAuthToken):
            accessToken = oauth.OAuthToken(
                                    accessToken['key'],
                                    accessToken['secret'])

        if not type:
            requestUrl = '/users/%s/rental_history' % (accessToken.key)
        else:
            requestUrl = '/users/%s/rental_history/%s' % (accessToken.key,type)
        
        try:
            info = simplejson.loads( self.client._getResource(
                                    requestUrl,
                                    parameters=parameters,
                                    token=accessToken))
        except:
            return {}
            
        return info
        

class NetflixCatalog():
    def __init__(self,client):
        self.client = client

    def searchTitles(self, term,startIndex=None,maxResults=None):
        requestUrl = '/catalog/titles'
        parameters = {'term': term}
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults
        info = simplejson.loads( self.client._getResource(
                                    requestUrl,
                                    parameters=parameters))

        return info['catalog_titles']['catalog_title']

    @property
    def index(self):
        requestUrl = '/catalog/titles/index'

        info = self.client._getResource(
                                    requestUrl,
                                    self.client.user.accessToken,
                                    {},
                                    True
                                    )

        return info

    def searchStringTitles(self, term,startIndex=None,maxResults=None):
        requestUrl = '/catalog/titles/autocomplete'
        parameters = {'term': term}
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults

        info = simplejson.loads(self.client._getResource(
                                    requestUrl,
                                    parameters=parameters))
        print simplejson.dumps(info)
        return info['autocomplete']['autocomplete_item']
    
    def getTitle(self, url):
        requestUrl = url
        info = simplejson.loads(self.client._getResource(requestUrl))
        return info

    def searchPeople(self, term,startIndex=None,maxResults=None):
        requestUrl = '/catalog/people'
        parameters = {'term': term}
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults

        try:
            info = simplejson.loads( self.client._getResource(
                                    requestUrl,
                                    parameters=parameters))
        except:
            return []

        return info['people']['person']

    def getPerson(self,url):
        requestUrl = url
        try:
            info = simplejson.loads(self.client._getResource(requestUrl))
        except:
            return {}
        return info

class NetflixUserQueue:
    def __init__(self,user):
        self.user = user
        self.client = user.client
        self.tag = None

    def getContents(self, sort=None, startIndex=None,
                                    maxResults=None, updatedMin=None):
        parameters={}
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults
        if updatedMin:
            parameters['updated_min'] = updatedMin
        if sort and sort in ('queue_sequence','date_added','alphabetical'):
            parameters['sort'] = sort
        
        requestUrl = '/users/%s/queues' % (self.user.accessToken.key)
        try:
            info = simplejson.loads(self.client._getResource(
                                    requestUrl,
                                    parameters=parameters,
                                    token=self.user.accessToken ))
        except:
            return []
        else:
            return info
            
    def getAvailable(self, sort=None, startIndex=None,
                                    maxResults=None, updatedMin=None,
                                    type='disc'):
        parameters={}
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults
        if updatedMin:
            parameters['updated_min'] = updatedMin
        if sort and sort in ('queue_sequence','date_added','alphabetical'):
            parameters['sort'] = sort

        requestUrl = '/users/%s/queues/%s/available' % (
                                    self.user.accessToken.key,
                                    type)
        try:
            info = simplejson.loads(self.client._getResource( 
                                    requestUrl,
                                    parameters=parameters,
                                    token=self.user.accessToken ))
        except:
            return []
        else:
            return info

    def getSaved(self, sort=None, startIndex=None, 
                                    maxResults=None, updatedMin=None,
                                    type='disc'):
        parameters={}
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults
        if updatedMin:
            parameters['updated_min'] = updatedMin
        if sort and sort in ('queue_sequence','date_added','alphabetical'):
            parameters['sort'] = sort

        requestUrl = '/users/%s/queues/%s/saved' % (
                                    self.user.accessToken.key,
                                    type)
        try:
            info = simplejson.loads(self.client._getResource(
                                    requestUrl,
                                    parameters=parameters,
                                    token=self.user.accessToken))
        except:
            return []
        else:
            return info
 
    def addTitle(self, discInfo=[], urls=[],type='disc',position=None):
        accessToken=self.user.accessToken
        parameters={}
        if position:
            parameters['position'] = position
            
        if not isinstance(accessToken, oauth.OAuthToken):
            accessToken = oauth.OAuthToken(
                                    accessToken['key'],
                                    accessToken['secret'])

        requestUrl = '/users/%s/queues/disc' % (accessToken.key)
        if not urls:
            for disc in discInfo:
                urls.append(disc['id'])
        parameters = {'title_ref': ','.join(urls)}

        if not self.tag:
            response = self.client._getResource(
                                    requestUrl, 
                                    token=accessToken)
            response = simplejson.loads(response)
            self.tag = response["queue"]["etag"]
        parameters['etag'] = self.tag
        response = self.client._postResource(
                                    requestUrl,
                                    token=accessToken,
                                    parameters=parameters)
        return response

    def removeTitle(self, id, type='disc'):
        accessToken=self.user.accessToken
        entryID = None
        parameters={}
        if not isinstance(accessToken, oauth.OAuthToken):
            accessToken = oauth.OAuthToken(
                                    accessToken['key'],
                                    accessToken['secret'])

        # First, we gotta find the entry to delete
        queueparams = {'max_results': 500}
        requestUrl = '/users/%s/queues/disc' % (accessToken.key)
        response = self.client._getResource(
                                    requestUrl,
                                    token=accessToken,
                                    parameters=queueparams)
        print "Response is " + response
        response = simplejson.loads(response)
        titles = response["queue"]["queue_item"]
        
        for disc in titles:
            discID = os.path.basename(urlparse(disc['id']).path)
            if discID == id:
                entryID = disc['id']

        if not entryID:
            return
        firstResponse = self.client._getResource(
                                    entryID,
                                    token=accessToken,
                                    parameters=parameters)
        
        response = self.client._deleteResource(entryID, token=accessToken)
        return response

class NetflixPerson:
    def __init__(self,personInfo,client):
        self.info = personInfo
        self.client = client

    @property
    def id(self):
        return self.info['id'].split('/')[-1]

    @property
    def name(self):
        return self.info['name']

    @property
    def filmography(self):
        raw_films = self.getInfo('filmography')['filmography']['filmography_item']

        if isinstance(raw_films, list):
            films = []
            for film in raw_films:
                films.append(NetflixDisc(film,self.client))
            return films
        else:
            return NetflixDisc(raw_films,self.client)

    def getInfo(self,field):
        fields = []
        url = ''
        for link in self.info['link']:
            fields.append(link['title'])
            if link['title'] == field:
                url = link['href']
        if not url:
            errorString = "Invalid or missing field.  " + \
                          "Acceptable fields for this object are:\n" + \
                          "\n\n".join(fields)
            print errorString
            sys.exit(1)
        try:
            info = simplejson.loads(self.client._getResource(url))
        except:
            return []
        else:
            return info

class NetflixDisc:
    def __init__(self,discInfo,client):
        self.info = discInfo
        self.client = client

    @property
    def id(self):
        return self.info['id'].split('/')[-1]

    @property
    def disc_number(self):
        raw_title = self.info['title']['regular']
        try:
            result = re.search(': Disc \d+$',raw_title)
            return int(result.group().strip(': Disc'))
        except AttributeError:
            return False

    @property
    def title(self):
        raw_title = self.info['title']['regular']
        title = re.split(': Disc \d+$',raw_title)[0]
        return title

    @property
    def length(self):
        seconds = int(self.info['runtime'])
        return seconds/60

    @property
    def mpaa_rating(self):
        for i in self.info['category']:
            if i['scheme'] == 'http://api.netflix.com/categories/mpaa_ratings':
                return i['term']
        return None

    @property
    def tv_rating(self):
        for i in self.info['category']:
            if i['scheme'] == 'http://api.netflix.com/categories/tv_ratings':
                return i['term']
        return None

    @property
    def formats(self):
        raw_formats = self.getInfo('formats')['delivery_formats']['availability']
        if isinstance(raw_formats, list):
            formats = []
            for format in raw_formats:
                format_name = format['category']['term']
                release_date = datetime.fromtimestamp(float(format['available_from']))
                formats.append({'format':format_name, 'release_date': release_date})
            return formats
        else:
            format_name = raw_formats['category']['term']
            release_date = datetime.fromtimestamp(float(raw_formats['available_from']))
            return [{'format':format_name, 'release_date': release_date}]

    @property
    def directors(self):
        raw_directors = self.getInfo('directors')
        raw_directors = raw_directors['people']['person']
        if isinstance(raw_directors, list):
            directors = []
            for director in raw_directors:
                directors.append(NetflixPerson(director, self.client))
            return directors
        else:
            return NetflixPerson(raw_directors, self.client)

    @property
    def cast(self):
        raw_cast = self.getInfo('cast')
        raw_cast = raw_cast['people']['person']
        if isinstance(raw_cast, list):
            people = []
            for person in raw_cast:
                people.append(NetflixPerson(person, self.client))
            return people
        else:
            return NetflixPerson(raw_cast, self.client)

    @property
    def release_year(self):
        try:
            return self.info['release_year']
        except KeyError:
            return None

    @property
    def shipped_date(self):
        try:
            return datetime.fromtimestamp(float(self.info['shipped_date']))
        except KeyError:
            return None

    def getInfo(self,field):
        fields = []
        url = ''
        for link in self.info['link']:
            fields.append(link['title'])
            if link['title'] == field:
                url = link['href']
        if not url:
            errorString = "Invalid or missing field.  " + \
                          "Acceptable fields for this object are:\n" + \
                          "\n\n".join(fields)
            print errorString
            sys.exit(1)
        try:
            info = simplejson.loads(self.client._getResource(url))
        except:
            return []
        else:
            return info

class NetflixClient:
    def __init__(self, name, key, secret, callback='',verbose=False):
        self.connection = httplib.HTTPConnection(HOST, PORT)
        self.server = HOST
        self.verbose = verbose
        self.user = None
        self.catalog = NetflixCatalog(self)
        
        self.CONSUMER_NAME=name
        self.CONSUMER_KEY=key
        self.CONSUMER_SECRET=secret
        self.CONSUMER_CALLBACK=callback
        self.consumer = oauth.OAuthConsumer(
                                    self.CONSUMER_KEY,
                                    self.CONSUMER_SECRET)
        self.signature_method_hmac_sha1 = \
                                    oauth.OAuthSignatureMethod_HMAC_SHA1()

    def _getResource(self, url, token=None, parameters={}, xml=False):
        if not re.match('http',url):
            url = "http://%s%s" % (HOST, url)
        if not xml:
            parameters['output'] = 'json'
        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(
                                    self.consumer,
                                    http_url=url,
                                    parameters=parameters,
                                    token=token)
        oauthRequest.sign_request(  
                                    self.signature_method_hmac_sha1,
                                    self.consumer,
                                    token)

        if (self.verbose):
            print oauthRequest.to_url()

        headers = {'Accept-encoding':'gzip'}

        req = urllib2.Request(oauthRequest.to_url(), None, headers)
        response = urllib2.urlopen(req)
        data = gzip.GzipFile(fileobj=StringIO.StringIO(response.read())).read()
        return data

    def _postResource(self, url, token=None, parameters=None):
        if not re.match('http',url):
            url = "http://%s%s" % (HOST, url)

        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(
                                    self.consumer,
                                    http_url=url,
                                    parameters=parameters,
                                    token=token,
                                    http_method='POST')
        oauthRequest.sign_request(
                                    self.signature_method_hmac_sha1,
                                    self.consumer,
                                    token)

        if (self.verbose):
            print "POSTING TO" + oauthRequest.to_url()

        headers = {'Content-Type':'application/x-www-form-urlencoded',
                   'Accept-encoding':'gzip'}

        data = oauthRequest.to_postdata()
        req = urllib2.Request(oauthRequest.to_url(), data, headers)
        response = urllib2.urlopen(req)
        data = gzip.GzipFile(fileobj=StringIO.StringIO(response.read())).read()
        return data

    def _deleteResource(self, url, token=None, parameters=None):
        if not re.match('http',url):
            url = "http://%s%s" % (HOST, url)

        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(
                                    self.consumer,
                                    http_url=url,
                                    parameters=parameters,
                                    token=token,
                                    http_method='DELETE')
        oauthRequest.sign_request(
                                    self.signature_method_hmac_sha1,
                                    self.consumer,
                                    token)

        if (self.verbose):
            print "DELETING FROM" + oauthRequest.to_url()

        self.connection.request('DELETE', oauthRequest.to_url())
        response = self.connection.getresponse()
        return response.read()
