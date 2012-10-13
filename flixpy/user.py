from flixpy.base import NetflixBase

class NetflixUser(NetflixBase):
    def __init__(self, client, user_id=None):
        if user_id:
            self.id = user_id
        else:
            # if we don't have a user id, we need to request it from netflix
            # This is an extra request, so best to save it!
            result = client.get_resource('/users/current')
            self.id = result.values()[0].split('/')[-1]

        raw_json = client.get_resource('/users/%s' % self.id)

        super(NetflixUser, self).__init__(raw_json['user'], client)

    def __repr__(self):
        return self.id
