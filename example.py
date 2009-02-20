# Sample code to use the Netflix python client

from Netflix import *
import getopt
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

netflix = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK, verbose)
if usertoken:
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


discs=[]
for arg in args:
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

  ######################################
  # Use autocomplete to retrieve titles
  # starting with a specified string.
  # To view all of the returned object, 
  # you can add a simplejson.dumps(info)
  ######################################  
  print "*** First thing, we'll search for 'Coc' as a string and see if that works ***"
  autocomplete = netflix.catalog.searchStringTitles('Coc')
  print simplejson.dumps(autocomplete)
  for info in autocomplete:
	print info['title']['short']
	
  ######################################
  # Grab a specific title from the ID. 
  # The ID is available as part of the
  # results from most queries (including
  # the ones above.
  ######################################  
  print "*** Now we'll go ahead and try to retrieve a single movie via ID string ***"
  movie = netflix.catalog.getTitle("http://api.netflix.com/catalog/titles/movies/60002013")
  if movie['catalog_title']['title']['regular'] == "Flip Wilson":
	print "It's a match, woo!"

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

  ######################################
  # You can search for people or retrieve
  # a specific person once you know their
  # netflix ID
  ######################################  
  print "*** Searching for %s ***" % "Julia"
  person = netflix.catalog.searchPeople("Julia")
  if isinstance(person,dict):
  	print simplejson.dumps(person,indent=4)

  print "*** Now let's retrieve a person by ID ***"
  newPerson = netflix.catalog.getPerson("http://api.netflix.com/catalog/people/78726")
  if isinstance(newPerson,dict):
  	print simplejson.dumps(newPerson,indent=4)

if usertoken and discs:
	######################################
    # Ratings are available from each disc,
    # or if you've got a specific user you
    # can discover their rating, expected
    # rating
    ######################################  
  
	print "*** Let's grab some ratings for all the titles that matched initially ***"
	ratings =  netflix.user.getRatings( discs )
	print "ratings = %s" % (simplejson.dumps(ratings,indent=4))
else:
	print "*** No authenticated user, so we'll just look at the average rating for the movies.***"
	for disc in discs:
		print "%s : %s" % (disc['title']['regular'],disc['average_rating'])

######################################
# User functions.  There are a lot.
######################################  	
if usertoken:
	print "*** Who is this person? ***"
	user = netflix.user.getData()
	print "%s %s" % (user['first_name'], user['last_name'])
	print simplejson.dumps(user,indent=4)
	
	######################################
	# User subinfo is accessed similarly
	# to disc subinfo.  Find the field
	# describing the thing you want, then
	# retrieve that url and get that info
	######################################
	print "*** What are their feeds? ***"
	feeds = netflix.user.getInfo('feeds')
	print simplejson.dumps(feeds,indent=4)
	
	print "*** Do they have anything at home? ***"
	feeds = netflix.user.getInfo('at home')
	print simplejson.dumps(feeds,indent=4)
	
	print "*** Show me their recommendations ***"
	recommendations = netflix.user.getInfo('recommendations')
	print simplejson.dumps(recommendations,indent=4)
	
	
	######################################
	# We need to fix up this queue stuff 
	# so that a queue is an object with
	# adding, deleting, shuffling around
	# methods
	######################################
	if queuedisc:
		if not usertoken:
			print "Unable to add to queue without authorization.  Use -a to authorize."
		else:
			print netflix.user.queueDiscs( urls=["http://api.netflix.com/catalog/titles/movies/60002013"])

	# Simple rental history
	history = netflix.user.getRentalHistory()
	print simplejson.dumps(history,indent=4)
	
	# A little more complicated, let's use mintime to get recent shipments
	history = netflix.user.getRentalHistory('shipped',updatedMin=1219775019,maxResults=4)
	print simplejson.dumps(history,indent=4)
  
	