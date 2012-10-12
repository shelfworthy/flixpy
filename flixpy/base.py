import logging

log = logging.getLogger('flixpy.base')

class NetflixBase(object):
    '''
    This is the base netflix object class that we will build
    netflix resources (title, user, person, etc.) on.
    '''
    def __init__(self, raw_json, client):
        self.data = raw_json
        self.client = client
