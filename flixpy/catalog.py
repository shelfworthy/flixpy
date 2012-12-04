from title import NetflixTitle

class NetflixCatalog(object):
    def __init__(self, client):
        self.client = client

    def streaming(self, *args, **kwargs):
        # NOTE this downloads *all* the streaming titles on netflix. This may take a while ;)
        return self.client.get_resource('/catalog/titles/streaming', *args, **kwargs)

    def _search(self, url, term, startIndex=None, maxResults=None, expand=None, show_disks=False):
        parameters = {
            'term': term,
        }

        if not show_disks:
            parameters['filters'] = '%s/categories/title_formats/instant' % self.client.server
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults

        return self.client.get_resource(url, parameters, expand=expand)

    def autocomplete(self, term, startIndex=None, maxResults=None):
        results = self._search('/catalog/titles/autocomplete', term, startIndex, maxResults)

        if results['autocomplete']:
            return results['autocomplete']['title']
        return []

    def search(self, term, startIndex=None, maxResults=None, expand=None):
        results = self._search('/catalog/titles', term, startIndex, maxResults, expand)

        try:
            return [NetflixTitle(title, self.client) for title in results['catalog']]
        except KeyError:
            return []
