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


		
netflix = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK)
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
  print "*** RETRIEVING MOVIES MATCHING %s ***" % arg
  data = netflix.catalog.searchTitles(arg)
  for info in data:
	print info['title']['regular']
	discs.append(info)

  testSubject = data[10]
  print simplejson.dumps(testSubject, indent=4)
  
  print "*** For demonstration purposes, we will arbitrarily pick the first result for the remaining tests ***"
  print "*** Retrieving additional information for %s ***" % (testSubject['title']['regular'])

  print "*** First thing, we'll search for 'Foo' as a string and see if that works ***"
  autocomplete = netflix.catalog.searchStringTitles('Foo')
  print simplejson.dumps(autocomplete)
  for info in autocomplete:
	print info['title']['short']
	
  print "*** Now we'll go ahead and try to retrieve the single movie via ID string ***"
  movie = netflix.catalog.getMovie(testSubject['id'])
  if movie['catalog_title']['title']['regular'] == testSubject['title']['regular']:
	print "It's a match, woo!"

  print "*** Let's grab the format for this movie ***"
  disc = NetflixDisc(testSubject,netflix)
  formats = disc.getInfo('formats')
  print "Formats: %s" % simplejson.dumps(formats,indent=4)

  print "*** And the synopsis ***"
  synopsis = disc.getInfo('synopsis')
  print "Synopsis: %s" % simplejson.dumps(synopsis, indent=4)

  if queuedisc:
		if not usertoken:
			print "Unable to add to queue without authorization.  Use -a to authorize."
		else:
			print netflix.user.queueDiscs( urls=[data['id']])

if usertoken and discs:
	print "*** Let's grab some ratings for all the titles that matched initially ***"
	ratings =  netflix.user.getRatings( discs )
	print "ratings = %s" % (simplejson.dumps(ratings,indent=4))
else:
	print "*** No authenticated user, so we'll just look at the average rating for the movies.***"
	for disc in discs:
		print "%s : %s" % (disc['title']['regular'],disc['average_rating'])