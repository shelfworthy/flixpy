import re
import httplib
import logging

import requests
from requests.auth import OAuth1

from .catalog import NetflixCatalog
from .user import NetflixUser

log = logging.getLogger('flixpy.client')

class NetflixClient(object):
    def __init__(self, application_name, client_key, client_secret, resource_owner_key=None, resource_owner_secret=None, callback=None, user_id=None):
        self.application_name = application_name
        self.server = 'api-public.netflix.com'
        self.connection = httplib.HTTPConnection(self.server, '80')

        # Setting up the OAuth client
        # This gets a little more complex than I would like because requests requries unicode.
        self.client_key = unicode(client_key)
        self.client_secret = unicode(client_secret)
        self.resource_owner_key = None
        self.resource_owner_secret = None
        if resource_owner_key:
            self.resource_owner_key = unicode(resource_owner_key)
        if resource_owner_secret:
            self.resource_owner_secret = unicode(resource_owner_secret)
        self.callback = None
        if callback:
            self.callback = unicode(callback)

        self.oauth = OAuth1(self.client_key, self.client_secret, self.resource_owner_key, self.resource_owner_secret, signature_type='query')

        if resource_owner_key and resource_owner_secret:
            # if we have access to a user, attach the user object
            self.user = NetflixUser(self, user_id)

        # Attach the netflix catalog functions
        self.catalog = NetflixCatalog(self)

        # setup a placeholder for the users instant queue
        self.instant_queue = None

    def _request(self, method, url, params=None, data=None, default_params=True):
        if not re.match('http', url):
            url = "http://%s%s" % (self.server, url)

        request_params = {}

        if default_params:
            request_params['output'] = u'json'
            request_params['v'] = u'2.0'
            # request_params['application_name'] = self.application_name
        if params:
            request_params = dict(request_params.items() + params.items())

        response = requests.request(method, url, params=request_params, data=data, allow_redirects=True, auth=self.oauth, headers={'Accept-encoding': 'gzip'})
        # raise an error if we get it
        response.raise_for_status()

        return response.json

    def get_resource(self, url, params=None, expand=None, **kwargs):
        if expand:
            if not params:
                params = {}
            params['expand'] = expand

        return self._request('get', url, params, **kwargs)

    def post_resource(self, url, params=None, data=None, **kwargs):
        return self._request('post', url, params, data, **kwargs)

    def delete_resource(self, url, params=None, **kwargs):
        return self._request('delete', url, params, **kwargs)

    # Auth

    def get_request_token_url(self):
        response = self.get_resource('/oauth/request_token')
        secret_and_token = (response['oauth_token_secret'], response['oauth_token'])

        url = response['login_url'] + '&application_name=%s&oauth_consumer_key=%s' % (response['application_name'], self.client_key)

        if self.callback:
            url += '&oauth_callback=%s' % self.callback

        return (secret_and_token, url)

    def get_access_token(self, secret, token):
        self.oauth = OAuth1(self.client_key, self.client_secret, token, secret, signature_type='auth_header')

        response = self.get_resource('/oauth/access_token')

        # connect this new user to this client
        self.oauth = OAuth1(self.client_key, self.client_secret, unicode(response['oauth_token']), unicode(response['oauth_token_secret']), signature_type='query')
        self.user = NetflixUser(self)

        return response

