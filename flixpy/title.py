from datetime import timedelta

from requests.exceptions import HTTPError

from .base import NetflixBase
from .person import NetflixPerson

class NetflixTitle(NetflixBase):
    @property
    def title(self):
        if isinstance(self.data['title'], dict):
            return self.data['title']['regular']
        return self.data['title']

    @property
    def synopsis(self):
        raw = self.get_info('synopsis')
        return raw['regular']

    # the following all assumes we're talking about streaming

    @property
    def is_available(self):
        raw = self.get_info('format_availability')

        if raw:
            return 'instant' in raw['delivery_formats']
        else:
            return False

    def _stream_info(self, key):
        if self.is_available:
            instant = self.get_info('format_availability')['delivery_formats']['instant']
            if key in instant:
                return instant[key]
        return None

    @property
    def mpaa_rating(self):
        return self._stream_info('mpaa_ratings')

    @property
    def tv_rating(self):
        return self._stream_info('tv_ratings')

    @property
    def is_hd(self):
        return self._stream_info('quality') == 'HD'

    @property
    def length(self):
        runtime = self._stream_info('runtime')

        if runtime:
            runtime = str(timedelta(seconds=runtime))

        return runtime

    @property
    def watch_link(self):
        if self.is_available:
            return 'https://movies.netflix.com/WiPlayer?movieid=%s' % self.id
        else:
            return None

    def directors(self):
        return [NetflixPerson(person, self.client) for person in self.get_info('directors')]

    def cast(self):
        return [NetflixPerson(person, self.client) for person in self.get_info('cast')]

    #####################
    #  Queue Functions  #
    #####################

    def remove_from_queue(self, second_try=False):
        if self.client.instant_queue:
            for item in self.client.instant_queue['queue']:
                if str(self.id) in item['id']:
                    try:
                        self.client.instant_queue = self.client.delete_resource(item['id'], params={'etag': self.client.instant_queue['meta']['etag']})
                        return True
                    except HTTPError:
                        # the queue is probably outdated, update and try again
                        if not second_try:
                            self.client.instant_queue = self.client.user.instant_queue(raw=True)
                            self.client.instant_queue = self.remove_from_queue(second_try=True)
        else:
            self.client.instant_queue = self.client.user.instant_queue(raw=True)
            self.remove_from_queue()
        return False

    def add_to_queue(self, position=None, second_try=False):
        if self.client.instant_queue:
            try:
                if not position:
                    # if we don't have a position, put this item at the end
                    position = int(self.client.instant_queue['meta']['queue_length']) + 1
                self.client.post_resource('/users/%s/queues/instant' % self.client.user.id, data={
                    'etag': self.client.instant_queue['meta']['etag'],
                    'title_ref': self.url,
                    'position': unicode(position)
                })

                self.client.instant_queue = self.client.user.instant_queue(raw=True)

                return True
            except HTTPError:
                if not second_try:
                    self.client.instant_queue = self.client.user.instant_queue(raw=True)
                    self.add_to_queue(position, second_try=True)
        else:
            self.client.instant_queue = self.client.user.instant_queue(raw=True)
            self.add_to_queue(position)

        return False

'''

    @property
    def series_title(self):
        if self.type == 'series':
            return self.title
        elif self.type != 'movie':
            return self.series().title
        return None

    @property
    def season_number(self):
        try:
            i = 1
            for season in self.series().seasons():
                if self.id == season.id:
                    return i
                else:
                    i += 1
        except TypeError:
            return None

    @property
    def episode_title(self):
        try:
            return self.info['title']['episode_short']
        except KeyError:
            return None

    @property
    def episode_number(self):
        try:
            i = 1
            for episode in self.season().episodes():
                if self.id == episode.id:
                    return i
                else:
                    i += 1
        except TypeError:
            return None




    @property
    def tv_rating(self):
        for i in self.info['category']:
            if i['scheme'] == 'http://api.netflix.com/categories/tv_ratings':
                return i['term']
        return None



    # deeper info about an item (requires more queries of the netflix api)

    def directors(self):
        raw_directors = self.get_info('directors')
        raw_directors = raw_directors['people']['person']
        if isinstance(raw_directors, list):
            directors = []
            for director in raw_directors:
                directors.append(NetflixPerson(director, self.client))
            return directors
        else:
            return NetflixPerson(raw_directors, self.client)

    def cast(self):
        raw_cast = self.get_info('cast')
        raw_cast = raw_cast['people']['person']
        if isinstance(raw_cast, list):
            return [NetflixPerson(person, self.client) for person in raw_cast]
        else:
            return NetflixPerson(raw_cast, self.client)

    def bonus_material(self):
        raw_bonus = self.get_info('bonus materials')
        if raw_bonus:
            return [self.client.catalog.title(title['href']) for title in raw_bonus['bonus_materials']['link']]
        else:
            return []

    def similar_titles(self):
        raw_sim = self.get_info('similars')
        if raw_sim:
            raw_sim = raw_sim['similars']['similars_item']

            if isinstance(raw_sim, list):
                return [NetflixTitle(title,self.client) for title in raw_sim]
            else:
                return NetflixTitle(raw_sim, self.client)
        else:
            return []

    def user_state(self):
        user = self.client.user

        try:
            return json.loads(
                self.client._get_resource(
                    url=user.get_info('title states')['title_states']['url_template'].split('?')[0],
                    token=user.accessToken,
                    parameters={'title_refs':self.id}
                )
            )
        except:
            return []
'''
