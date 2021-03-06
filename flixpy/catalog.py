from title import NetflixTitle

class NetflixCatalog(object):
    def __init__(self, client):
        self.client = client

    def streaming(self, *args, **kwargs):
        # NOTE this downloads *all* the streaming titles on netflix. This may take a while ;)
        return self.client.get_resource('/catalog/titles/streaming', *args, **kwargs)

    def _search(self, url, term, expand=None, parameters=None):
        if not parameters:
            parameters = {}

        parameters['term'] = term

        return self.client.get_resource(url, parameters, expand=expand)

    def autocomplete(self, term):
        results = self._search('/catalog/titles/autocomplete', term)

        if results['autocomplete']:
            return results['autocomplete']['title']
        return []

    def search(self, term, startIndex=None, maxResults=None, expand=None, show_disks=False):
        parameters = {}

        if not show_disks:
            parameters['filters'] = '%s/categories/title_formats/instant' % self.client.server
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults

        results = self._search('/catalog/titles', term, expand, parameters)

        try:
            return [NetflixTitle(title, self.client) for title in results['catalog']]
        except KeyError:
            return []

    def get_title_by_id(self, netflix_id, expand=None):
        ''' get a title object using the titles netflix id (partial url):
            /catalog/titles/movies/60021896
        '''
        raw_title = self.client.get_resource(netflix_id, expand=expand)

        title = NetflixTitle(raw_title['catalog_title'], self.client)
        title.meta = raw_title['meta']

        return title
