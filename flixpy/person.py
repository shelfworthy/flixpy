from .base import NetflixBase

class NetflixPerson(NetflixBase):
    def __repr__(self):
        return self.full_name

    @property
    def full_name(self):
        return self.name

    def filmography(self):
        from .title import NetflixTitle

        return [NetflixTitle(title, self.client) for title in self.get_info('filmography')]
