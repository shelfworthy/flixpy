import logging

log = logging.getLogger('flixpy.base')

class NetflixBase(object):
    '''
    This is the base netflix object class that we will build
    netflix resources (title, user, person, etc.) on.
    '''
    def __init__(self, raw_json, client):
        self.client = client

        self.data = raw_json
        self.meta = None

    def __getattr__(self, name):
        return self.get_info(name)

    @property
    def id(self):
        return int(self.data['id'].split('/')[-1])

    @property
    def url(self):
        return self.data['id']

    @property
    def type(self):
        '''
        get the item type:
            movie
            series
            season
            episode (netflix calles this program, which is dumb)
            person
            user
        '''
        raw = self.url.split('/')[-2]

        if raw == 'people':
            return 'person'
        elif raw != 'series':
            # remove the 's' from the end of everything but series
            return self.url.split('/')[-2][0:-1]
        else:
            return raw

    @property
    def _resource(self):
        '''
        The key for the dict that stores data for this item type
        '''

        if self.type in ['movie', 'series', 'season', 'episode']:
            return 'catalog_title'
        return self.type

    def get_info(self, key, result_key=None, params=None):
        '''
        This function will get the given key from the resource.
        If the data has already been downloaded, its returned.
        If the data hasn't been downloaded, this function hits
        the server to fill out more data about this item.

        key: the key to get info from
        result_key: if the key to request and the key results are differnt, send the result key here

        '''

        if key in self.data:
            return self.data[key]
        else:
            # first we should make sure we have the complete resource (and not just a search result)
            if not self.meta:
                full_data = self.client.get_resource(self.url)
                self.meta = full_data['meta']
                self.data = full_data[self._resource]

            # see if what the user is looking for is still on the server
            if 'links' in self.meta and key in self.meta['links']:
                resource = self.client.get_resource(self.meta['links'][key], params=params)

                if resource:
                    try:
                        self.data[key] = resource[result_key or key]
                    except KeyError:
                        try:
                            self.data[key] = self.client.get_resource(self.meta['links'][key])
                        except KeyError:
                            self.data[key] = None

        return self.data[key]
