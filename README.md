predictimdb
===========

Python tools to scrape data from IDMB and predict movie revenue!

In the data folder, you have raw, unparsed data retrieved by the scraper.

The data is stored as a JSON encoded list of dictionaries. Each movie is a dictionary with the following fields:


	      'name' : string, movie name
	      'mpaa' : string, MPAA rating
	      'link' : string, link to IMDB movie page
	      ‘year' : string, release year
	      ‘runtime' : string, length of movie in minutes
	      ‘revenue' : string, US box office revenue of movie
	      'stars' : list of name-URL dictionaries
              'directors' : list of name-URL dictionaries
              'writers' : list of name-URL dictionaries
              'budget' : string, filming budget given by IMDB
              'genres' : list of strings
              'castlist' : list of strings, cast names
              'release' : string, release date
              'countries' : list of strings
              'tagline' : string, brief line about the movie
              'production' : list of name-URL dictionaries
              'userscore' : dictionary with fields ‘score' and ‘count'
              'metascore' : string, metascore as given by IMDB

A name-URL dictionary refers to a dictionary with the fields ‘name' and ‘url’. The ‘name' is simply the name of the entity and the ‘url' is the url to the IMDB page for that entity . The purpose of this is that if we want to get more metadata on any of the entities, we can. NOTE: any of these fields may be empty - check before referencing


