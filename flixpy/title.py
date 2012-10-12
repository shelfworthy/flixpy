from flixpy.base import NetflixBase

class NetflixTitle(NetflixBase):
    # helper functions for parent and child functions
    def _get_title_single(self, url):
        return NetflixTitle(self.getInfo(url)['catalog_title'], self.client)

    def _get_title_list(self, url):
        try:
            return [NetflixTitle(title, self.client) for title in self.getInfo(url)['catalog_titles']['catalog_title']]
        except TypeError:
            return []

    # These functions get the items parents, if they exist

    def season(self):
        return self._get_title_single(SEASON_URL)

    def series(self):
        return self._get_title_single(SERIES_URL)

    # These functions get the items children, if they exist

    def seasons(self):
        return self._get_title_list(SEASONS_URL)

    def episodes(self):
        return self._get_title_list(EPISODES_URL)

    # These functions deal with the current items details

    def __repr__(self):
        return self.title

    @property
    def id(self):
        return self.getInfoLink(TITLE_URL) or self.info['id']

    @property
    def int_id(self):
        return self.info['id'].split('/')[-1]

    @property
    def type(self):
        '''
        get the item type:
            movie
            series
            season
            episode (netflix calles this program, which is dumb)
        '''
        raw = self.id.split('/')[-2]
        if raw != 'series':
            # remove the 's' from the end of everything but series
            return self.id.split('/')[-2][0:-1]
        else:
            return raw

    @property
    def title(self):
        return self.info['title']

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
    def length(self):
        seconds = int(self.info['runtime'])
        return seconds/60

    @property
    def rating(self):
        if

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

    # deeper info about an item (requires more queries of the netflix api)

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

    def cast(self):
        raw_cast = self.getInfo('cast')
        raw_cast = raw_cast['people']['person']
        if isinstance(raw_cast, list):
            return [NetflixPerson(person, self.client) for person in raw_cast]
        else:
            return NetflixPerson(raw_cast, self.client)

    def bonus_material(self):
        raw_bonus = self.getInfo('bonus materials')
        if raw_bonus:
            return [self.client.catalog.title(title['href']) for title in raw_bonus['bonus_materials']['link']]
        else:
            return []

    def similar_titles(self):
        raw_sim = self.getInfo('similars')
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
                self.client._getResource(
                    url=user.getInfo('title states')['title_states']['url_template'].split('?')[0],
                    token=user.accessToken,
                    parameters={'title_refs':self.id}
                )
            )
        except:
            return []
'''
