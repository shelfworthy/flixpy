import re
import gzip
import httplib
import logging
import StringIO

import requests
from oauth_hook import OAuthHook

from flixpy.catalog import NetflixCatalog

log = logging.getLogger('flixpy.client')

class NetflixClient(object):
    def __init__(self, application_name, consumer_key, consumer_secret, token_key=None, token_secret=None):
        self.application_name = application_name
        self.server = 'api-public.netflix.com'
        self.connection = httplib.HTTPConnection(self.server, '80')

        # Setting up the OAuth client
        OAuthHook.consumer_key = consumer_key
        OAuthHook.consumer_secret = consumer_secret
        if token_key and token_secret:
            OAuthHook.access_token = token_key
            OAuthHook.access_token_secret = token_secret

            #    self.user = NetflixUser()
            # else:
            #    self.user = None

        oauth_hook = OAuthHook()
        self.client = requests.session(
            hooks={'pre_request': oauth_hook},
            headers={'Accept-encoding': 'gzip'},
        )

        self.catalog = NetflixCatalog(self)

    def _request(self, method, url, params=None, default_params=True):
        if not re.match('http', url):
            url = "http://%s%s" % (self.server, url)

        request_params = {}

        if default_params:
            request_params['output'] = 'json'
            request_params['v'] = 2.0
            # request_params['application_name'] = self.application_name
        if params:
            request_params = dict(request_params.items() + params.items())

        response = self.client.request(method, url, data=request_params, allow_redirects=True)
        response = requests.get(response.url)

        # raise an error if we get it
        response.raise_for_status()

        return response.json

    def get_resource(self, url, params=None, default_params=True):
        return self._request('get', url, params, default_params)

    def post_resource(self, url, params=None):
        return self._request('post', url, params)

    def delete_resource(self, url, params=None):
        return self._request('delete', url, params)

