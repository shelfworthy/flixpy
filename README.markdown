About
-----

This code is desgined to make working with netflix's streaming API easy. We take the pure json output of the netflix API and wrap it in a format that is easy to consume in python.

This code started out as a branch of [pyflix] (http://code.google.com/p/pyflix/)

*This is a work in progress.*

install
-------

`pip install flixpy`

setup
-----

First you'll need to get a `key` and `secret` from netflix. you can do that by registering here: http://developer.netflix.com/member/register

Once you have those (and have registered an app with them) you can get started. At the most basic level you can access general netflix resources using just the data provided above:

``` python
    from netflix import NetflixClient

    APP_NAME   = '<your app name>'
    API_KEY    = '<your key>'
    API_SECRET = '<your secret>'

    netflix = NetflixClient(APP_NAME, API_KEY, API_SECRET)
```

You can then do anything that dosn't require a netflix user. An example is `autocomplete`:

``` python

results = netflix.catalog.autocomplete('batman')

print results

[u'Batman: The Animated Series',
 u'Batman Beyond',
 u'Batman: The Brave and The Bold',
 ...

```

*Note that autocomplete only returns title strings. You can then use these in search to get exact matches with more data.*

Or do an actual search:

``` python

results = netflix.catalog.search('invader zim')

print [i.title for i in results]

[u'Invader Zim',
 u'Invader',
 u'The Invader',
 u'Invisible Invaders',
 ...
```

The catalog search returns NetflixTitle objects instead of strings. This way you can use them to get more information:

``` python

zim = netflix.catalog.search('invader zim')[0]
zim.synopsis

u'Zim, a pint-sized alien with an attitude, decides to single-handedly conquer the human race. Standing in his way is a paranoid kid named Dib. Since neither of them is exactly competent, their confrontations tend to result in disaster.'

zim.available

True  # this title is availble for streaming

zim.watch_link

'https://movies.netflix.com/WiPlayer?movieid=70202354'

```

More Coming Soon!
