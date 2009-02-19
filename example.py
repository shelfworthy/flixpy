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
		
APP_NAME   = 'Movie browser'
API_KEY    = 'nbf4kr594esg4af25qexwtnu'
API_SECRET = 'SSSeTdsPsM'
CALLBACK   = 'http://www.synedra.org'

EXAMPLE_USER = {
        'request': {
                'key': 'hwq8evzp4z2btfx5en9pfkvt',
                'secret': 'btrdgnyQcVxZ'
        },
        'access': {
                'key': 'T1lSMROEioV5Fio4RCWnRgSKe2pqg.W7pOgp8jBlf_Z5CUp0_9CtnXOpU.iVC4uw8U7qkD4BmEZIZfTyJcJWfe6Q--',
                'secret': 'RjQcVfVvyPnZ'
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
  data = netflix.catalog.searchMovieTitles(arg)
  for info in data['catalog_titles']['catalog_title']:
	print info['title']['regular']
	discs.append(info)

  testSubject = data['catalog_titles']['catalog_title'][10]
  print simplejson.dumps(testSubject, indent=4)
  
  print "*** For demonstration purposes, we will arbitrarily pick the first result for the remaining tests ***"
  print "*** Retrieving additional information for %s ***" % (testSubject['title']['regular'])

  print "*** First thing, we'll search for 'Foo' as a string and see if that works ***"
  autocomplete = netflix.catalog.searchStringMovieTitles('Foo')
  print simplejson.dumps(autocomplete)
  for info in autocomplete['autocomplete']['autocomplete_item']:
	print info['title']['short']
	
  print "*** Now we'll go ahead and try to retrieve the single movie via ID string ***"
  movie = netflix.catalog.getMovie(testSubject['id'])
  if movie['catalog_title']['title']['regular'] == testSubject['title']['regular']:
	print "It's a match, woo!"

  print "*** Let's grab the format for this movie ***"
  disc = NetflixDisc(testSubject,netflix)
  formats = disc.getAvailableFormats()
  print "Formats: %s" % simplejson.dumps(formats,indent=4)

  print "*** And the synopsis ***"
  synopsis = disc.getSynopsis()
  print "Synopsis: %s" % simplejson.dumps(synopsis, indent=4)

  if queuedisc:
		if not usertoken:
			print "Unable to add to queue without authorization.  Use -a to authorize."
		else:
			print netflix.user.queueDiscs( urls=[data['id']])

print "*** Let's grab some ratings for all the titles that matched initially ***"
if usertoken and discs:
	ratings =  netflix.user.getRatings( discs )
	print "ratings = %s" % (simplejson.dumps(ratings,indent=4))