from flixpy.base import NetflixBase

from .title import NetflixTitle

class NetflixUser(NetflixBase):
    def __init__(self, client, user_id=None):
        if user_id:
            self.id = user_id
        else:
            # if we don't have a user id, we need to request it from netflix
            # This is an extra request, so best to save it!
            result = client.get_resource('/users/current')
            self.id = result.values()[0].split('/')[-1]

        raw_json = client.get_resource(self.url)

        super(NetflixUser, self).__init__(raw_json['user'], client)

    def __repr__(self):
        return self.first_name + " %s" % self.last_name

    @property
    def url(self):
        return '/users/%s' % self.id

    def instant_queue(self):
        '''
        This is a quick link to the users instant queue. You can also get This
        by calling the `queue_list` resource, then calling the queue
        but thats an extra request.

        This function also expands the results with @title as the normal queue only sends id's
        '''

        item_list = self.client.get_resource('%s/queues/instant' % self.url, expand="@title")

        return [NetflixTitle(title['item'], self.client) for title in item_list['queue']]
