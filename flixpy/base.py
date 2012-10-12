import logging

log = logging.getLogger('flixpy.base')

class NetflixBase(object):
    '''
    This is the base netflix object class that we will build
    netflix resources (title, user, person, etc.) on.
    '''
    def __init__(self, raw_json, client):
        self.info = raw_json
        self.client = client

    def getInfo(self, field):
        url = ''
        fields = []

        for link in self.info['link']:
            fields.append('title: %s | rel: %s' % (link['title'], link['rel']))
            if link['title'] == field or link['rel'] == field:
                url = link['href']

        if not url:
            errorString = "Invalid or missing field.  " + \
                          "Acceptable fields for this object are:\n" + \
                          "\n\n".join(fields)
            log.debug(errorString)
            return None

        return self.client.getResource(url)

    def getInfoLink(self, field):
        for link in self.info['link']:
            if field in [link['title'], link['rel']]:
                return link['href']

        return None
