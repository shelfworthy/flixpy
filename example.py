# Sample code to use the Netflix python client

from Netflix import *
import getopt
import time 

APP_NAME   = ''
API_KEY    = ''
API_SECRET = ''
CALLBACK   = ''
        
EXAMPLE_USER = {
        'request': {
                'key': '',
                'secret': ''
        },
        'access': {
                'key': '',
                'secret': ''
        }
}

APP_NAME   = 'Movie browser'
API_KEY    = 'nbf4kr594esg4af25qexwtnu'
API_SECRET = 'SSSeTdsPsM'
CALLBACK   = 'http://www.synedra.org'

EXAMPLE_USER = {
        'request': {
                'key': 'guzwtx7epxmbder6dx5n2t7a',
                'secret': 'D8HrxmaQ7YRr'
        },
        'access': {
                'key': 'T1i0pqrkyEfVCl3NVbrSCMvFg0fPup3TsQ7bAQjN35XZcmuS9WDK7oVOkZdE6iGg8HkhEp4VQn7sSB.kILNu2HiQ--',
                'secret': 'efMFPEPZ35f6'
        }
}

def getAuth(netflix, verbose):
    netflix.user = NetflixUser(EXAMPLE_USER,netflix)
    
    if EXAMPLE_USER['request']['key'] and not EXAMPLE_USER['access']['key']:
      tok = netflix.user.getAccessToken( EXAMPLE_USER['request'] )
      print "now put this key / secret in EXAMPLE_USER.access so you don't have to re-authorize again:\n 'key': '%s',\n 'secret': '%s'\n" % (tok.key, tok.secret)
      EXAMPLE_USER['access']['key'] = tok.key
      EXAMPLE_USER['access']['secret'] = tok.secret
      sys.exit(1)

    elif not EXAMPLE_USER['access']['key']:
      (tok, url) = netflix.user.getRequestToken()
      print "Authorize user access here: %s" % url
      print "and then put this key / secret in EXAMPLE_USER.request:\n 'key': '%s',\n 'secret': '%s'\n" % (tok.key, tok.secret)
      print "and run again."
      sys.exit(1)
    return netflix.user

def doSearch(netflix, discs, arg):
    ######################################
    # Search for titles matching a string.
    # To view all of the returned object, 
    # you can add a simplejson.dumps(info)
    ######################################  
    print "*** RETRIEVING MOVIES MATCHING %s ***" % arg
    data = netflix.catalog.searchTitles(arg,1,10)
    for info in data:
        print info['title']['regular']
        discs.append(info)

def doAutocomplete(netflix,arg):
    ######################################
    # Use autocomplete to retrieve titles
    # starting with a specified string.
    # To view all of the returned object, 
    # you can add a simplejson.dumps(info)
    ######################################  
    print "*** First thing, we'll search for " + arg + " as a string and see if that works ***"
    autocomplete = netflix.catalog.searchStringTitles(arg)
    print simplejson.dumps(autocomplete)
    for info in autocomplete:
        print info['title']['short']
    
def getTitleFromID(netflix,arg):
    ######################################
    # Grab a specific title from the ID. 
    # The ID is available as part of the
    # results from most queries (including
    # the ones above.
    ######################################  
    print "*** Now we'll go ahead and try to retrieve a single movie via ID string ***"
    print "Checking for " + arg
    movie = netflix.catalog.getTitle(arg)
    if movie['catalog_title']['title']['regular'] == "Flip Wilson":
        print "It's a match, woo!"
    return movie

def getTitleInfo(netflix,movie):
    ######################################
    # You can retrieve information about 
    # a specific title based on the 'links'
    # which include formats, synopsis, etc.
    ######################################  
    print "*** Let's grab the format for this movie ***"
    disc = NetflixDisc(movie['catalog_title'],netflix)
    formats = disc.getInfo('formats')
    print "Formats: %s" % simplejson.dumps(formats,indent=4)

    print "*** And the synopsis ***"
    synopsis = disc.getInfo('synopsis')
    print "Synopsis: %s" % simplejson.dumps(synopsis, indent=4)

    print "*** And the cast ***"
    cast = disc.getInfo('cast')
    print "Cast: %s" % simplejson.dumps(cast, indent=4)

def findPerson(netflix, arg, id):
    ######################################
    # You can search for people or retrieve
    # a specific person once you know their
    # netflix ID
    ######################################  
    print "*** Searching for %s ***" % arg
    person = netflix.catalog.searchPeople(arg)
    if isinstance(person,dict):
        print simplejson.dumps(person,indent=4)
    elif isinstance(person,list):
        print simplejson.dumps(person[0],indent=4)
    else:
        print "No match"

    print "*** Now let's retrieve a person by ID ***"
    newPerson = netflix.catalog.getPerson(id)
    if isinstance(newPerson,dict):
        print simplejson.dumps(newPerson,indent=4)

def getRatings(netflix,user, discs):
    ######################################
    # Ratings are available from each disc,
    # or if you've got a specific user you
    # can discover their rating, expected
    # rating
    ######################################  
    if (user):
        print "*** Let's grab some ratings for all the titles that matched initially ***"
        ratings =  user.getRatings( discs )
        print "ratings = %s" % (simplejson.dumps(ratings,indent=4))
    else:
        print "*** No authenticated user, so we'll just look at the average rating for the movies.***"
        for disc in discs:
            print "%s : %s" % (disc['title']['regular'],disc['average_rating'])


def getUserInfo(netflix,user):
    print "*** Who is this person? ***"
    userData = user.getData()
    print "%s %s" % (userData['first_name'], userData['last_name'])
    
    ######################################
    # User subinfo is accessed similarly
    # to disc subinfo.  Find the field
    # describing the thing you want, then
    # retrieve that url and get that info
    ######################################
    print "*** What are their feeds? ***"
    feeds = user.getInfo('feeds')
    print simplejson.dumps(feeds,indent=4)

    print "*** Do they have anything at home? ***"
    feeds = user.getInfo('at home')
    print simplejson.dumps(feeds,indent=4)

    print "*** Show me their recommendations ***"
    recommendations = user.getInfo('recommendations')
    print simplejson.dumps(recommendations,indent=4)

    ######################################
    # Rental History
    ######################################
    # Simple rental history
    history = netflix.user.getRentalHistory()
    print simplejson.dumps(history,indent=4)

    # A little more complicated, let's use mintime to get recent shipments
    history = netflix.user.getRentalHistory('shipped',updatedMin=1219775019,maxResults=4)
    print simplejson.dumps(history,indent=4)

def userQueue(netflix,user):
    ######################################
    # Here's a queue.  Let's play with it
    ######################################
    queue = NetflixUserQueue(netflix.user)
    print "*** Add a movie to the queue ***"
    print simplejson.dumps(queue.getContents(), indent=4)
    print queue.addTitle( urls=["http://api.netflix.com/catalog/titles/movies/60002013"] )
    print "*** Move it to the top! ***"
    print queue.addTitle( urls=["http://api.netflix.com/catalog/titles/movies/60002013"], position=1 )
    print "*** Take it out ***"
    print queue.removeTitle( id="60002013")
    
    discAvailable = queue.getAvailable('disc')
    print  "discAvailable" + simplejson.dumps(discAvailable)
    instantAvailable =  queue.getAvailable('instant')
    print "instantAvailable" + simplejson.dumps(instantAvailable)
    discSaved =  queue.getSaved('disc')
    print "discSaved" + simplejson.dumps(discSaved)
    instantSaved = queue.getSaved('instant')
    print "instantSaved" + simplejson.dumps(instantSaved)
    
if __name__ == '__main__':  
    try:
            opts, args = getopt.getopt(sys.argv[1:], "qva")
    except getopt.GetoptError, err:
            # print help information and exit:
            print str(err) # will print something like "option -a not recognized"
            sys.exit(2)

    queuedisc=False
    verbose = False
    usertoken = False
    for o, a in opts:
        if o == "-v":
            verbose = True
        if o == "-q":
            queuedisc = True
        if o == '-a':
            usertoken = True

    netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK, verbose)
    if usertoken:
        user = getAuth(netflixClient,verbose)
    else:
        user = None
    discs=[]
    
    # Basic search functions
    for arg in args:
        doSearch(netflixClient,discs,arg)

    # Note that we have to sleep between queries to avoid the per-second cap on the API
    time.sleep(1)
    doAutocomplete(netflixClient,'Coc')
    time.sleep(1)
    movie = getTitleFromID(netflixClient,'http://api.netflix.com/catalog/titles/movies/60002013')
    time.sleep(1)
    getTitleInfo(netflixClient,movie)
    time.sleep(1)
    findPerson(netflixClient,"Harrison Ford", "http://api.netflix.com/catalog/people/78726")
    
    # Ratings (with/without user)
    if discs:
        getRatings(netflixClient,user, discs)
        time.sleep(1)
        
    # User functions
    if user:
        getUserInfo(netflixClient,user)
        time.sleep(1)
        userQueue(netflixClient,user)