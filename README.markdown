pyflix readme
-------------

This is a branch of [pyflix] (http://code.google.com/p/pyflix/) that's goal is to make the python API easer to work with.
The goal is to take pure json output and instead output formats that make sense with the data that is being requested.

*This is a work in progress.* Currently the User, Disk, and Person objects have gotten the most work, along with the at_home queue.
The example currently only shows how to work with the code in the old way at the moment (which should continue to work).
I hope to have time to update it soon.

for now here are some examples of how my interface works once you have an authenticated user (you can authenticate, for now, using the existing example.py)

bugs
----

As I'm not exactly the best python programmer, I'm sure there will be bugs and suggestions. Please fork and help out if you are able.
If you found something you aren't sure how to fix or have feature suggestions, please be feel to visit [lighthouse] (http://chrisdrackett.lighthouseapp.com/projects/29770-pyflix) and open a ticket.

install
-------

make sure you have [simplejson] (https://svn.red-bean.com/bob/simplejson/tags/simplejson-1.3/docs/index.html) installed (if you are using django, like I am, you have simplejson already!)

just make sure netflix.py is on your python path.

setup
-----

    from netflix import *
    
    APP_NAME   = '<your app name>'
    API_KEY    = '<your key>'
    API_SECRET = '<your secret>'
    CALLBACK   = '<your callback url>'
    verbose    = False
    
    EXAMPLE_USER = {
        'request': {
            'key': '<request key>',
            'secret': '<request secret>'
        },
        'access': {
                'key': '<access key>',
                'secret': '<access secret>'
        }
    }
    
    netflix = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK, verbose)
    
    netflix.user = NetflixUser(EXAMPLE_USER, netflix)

example usage
-------------

    ### we can get info on our current user:
    
    >> netflix.user.name
    u'Chris Drackett'
    
    >> netflix.user.preferred_formats
    [u'Blu-ray', u'DVD']
    
    >> netflix.user.can_instant_watch
    True
    
    ### what discs they currently have at home:
    
    >> movie = netflix.user.at_home[1]
    
    ### information about a movie:
    
    >> movie.title
    u'Cloverfield'
    
    >> movie.length
    84
    
    >> movie.mpaa_rating
    u'PG-13'
    
    >> movie.formats
    [{'format': u'DVD', 'release_date': datetime.datetime(2008, 4, 21, 19, 0)},
    {'format': u'Blu-ray', 'release_date': datetime.datetime(2008, 6, 2, 19, 0)}]
    
    >> movie.release_year
    u'2007'
    
    ### information about a person (in this case the director):
    
    >> movie.directors[0].name
    u'Matt Reeves'
    
    ### information about a person's filmography:
    
    >> movie.directors[0].filmography[0].title
    u'Cloverfield'
    
    >> movie.directors[0].filmography[0].title
    u'28 Weeks Later'
    
    ### information about a movies cast:
    
    >> movie.cast[0]
    u'Mike Vogel'
    
    ### see if the movie is part of a set (this one is not):
    
    >> movie.disc_number
    False
    
    ### lets find one that is:
    
    >> movie = netflix.user.at_home[2]
    
    >> movie.title
    u'Gilmore Girls: Season 5'
    
    ### lets find one that is:
    
    >> movie.disc_number
    5

    ### thats all for now!

Old Readme from pyflix on google code
-------------------------------------

Basic readme for the pyflix module.

In order to use the system, you need to get a developer key/secret from the Netflix developer site.  You will need those for all requests to Netflix.

To help you get a better understanding of how this works, here's a step by step tutorial.

1) Get a developer API key and secret
2) Put those values in the example.py script
3) Run the example.py script.  In this configuration it will perform all of the actions it can do without an authenticated user.
4) Run the example.py script with the "-a" flag.  Since you don't already have user keys, it will start the process of retrieving them.
5) Visit the website listed, and insert the request values into the example.py script under EXAMPLE_USER['request']
6) Run the example.py script again with the "-a" flag.  This will generate the access values.  Insert those into the script under EXAMPLE_USER['access']
7) At this point you can do any of the actions with example.py -a

In your own coding you may want to run these steps differently, or more silently.  You can retain the configuration within your application.  The example is somewhat clunky but should help you understand what can be done with the various levels of authentication.
