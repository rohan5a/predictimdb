import gc, bs4, time, json
from urllib2 import urlopen
from scraper import *

"""
attempts to read url and return HTML - will attempt
until recursion limit is reached (in case a bad read happens)
"""
def read_url(url):
    try: 
        html = urlopen(url, timeout=5).read()
    except: 
        print 'URL timed out. Trying again.'
        print 'URL: %s' % url
        time.sleep(3)
        return read_url(url)
    return html

"""
scrapes the data on a movie given the link to the IMDB movie page
called by scrape_links function (below)
"""
def scrape_movie_page(link):
    base = 'http://www.imdb.com'
    html = read_url(base+link)
    soup = bs4.BeautifulSoup(html)

    movie = { 'stars' : get_stars(soup),
              'directors' : get_directors(soup),
              'writers' : get_writers(soup),
              'budget' : get_budget(soup),
              'genres' : get_genres(soup),
              'castlist' : get_castlist(soup),
              'release' : get_release(soup),
              'countries' : get_countries(soup),
              'tagline' : get_tagline(soup),
              'production' : get_production(soup),
              'userscore' : get_userscore(soup),
              'metascore' : get_metascore(soup) }

    # print keys and values, for testing purposes
    # for key in movie.keys(): print key, movie[key], '\n'
    return movie

"""
calls scrape_movie_page to scrape movie data for each movie
link stored in links.json. saves 100 movies at a time
"""
def scrape_links(delay=1, savelimit=100):
    
    gc.enable()
    movies, full_movies, count = load_json('links.json'), [], 1

    for movie in movies:

        if count < 4601:
            print count
            count += 1
            continue

        time.sleep(delay)
        full_data = scrape_movie_page(movie['link'])

        movie.update(full_data)
        full_movies.append(movie)

        print count, movie['name'], movie['year'], movie['revenue']

        count += 1

        if count % savelimit == 0:
            rank = [str(count-savelimit), '-', str(count)]
            path = 'data/movies' + ' '.join(rank) + '.json'
            save_json(full_movies, path)
            full_movies = []
            gc.collect()
            print '%s ranked movies saved' % ' '.join(rank)

        # print keys and values, for testing purposes
        # for key in movie.keys(): print key, movie[key], '\n'

"""
parses the HTML for IMDB-ranked top box office movies; called
by scrape_many (this is a helper function that does the heavy lifting)
"""
def scrape_movies(url):

    html = read_url(url)
    soup = bs4.BeautifulSoup(html)
    titles = soup.findAll("td", "title")
    revenues = soup.findAll("td", "sort_col")
    movies, nullrev, STOP = [], 0, False

    for title, revenue in zip(titles, revenues):

        if str(revenue.string) == '-':
            nullrev += 1
            continue

        key = title.find("a") # get name and link
        name, link = key.text, key['href']

        try: year = title.find("span", "year_type").text
        except: year = '' # get release year

        try: runtime = (title.find("span", "runtime")).text
        except: runtime = '' # get runtime length

        try: mpaa = ((title.find("span", "certificate")).contents[0])['title']
        except: mpaa = '' # get MPAA rating

        movie = { 'name': name,
                  'mpaa': mpaa,
                  'link': link,
                  'year': year,
                  'runtime': runtime,
                  'revenue': revenue.string }

        movies.append(movie)
        print name, year, revenue.string

    if nullrev > 10: STOP = True
    return (movies, STOP)

"""
calls scrape_movies to get the movie page link and associated metadata
for top box office movies; saves output in links.json
"""
def scrape_many(start=1, step=50, delay=1):

    base = 'http://www.imdb.com/search/'
    sort = 'title?at=0&sort=boxoffice_gross_us,desc&start='

    movies = []
    while True:
        url = base + sort + str(start)
        output, stop = scrape_movies(url)
        movies.extend(output)
        if stop: break
        start += step
        print start
        time.sleep(delay)

    print '%d movies scraped' % len(movies)
    save_json(movies, 'links.json')

def save_json(movies, path):
    with open(path, 'w') as f: json.dump(movies, f, indent=4)

def load_json(path):
    with open(path, 'r') as f:
        movies = json.load(f)
    return movies
