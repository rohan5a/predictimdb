import sys, bs4, time, json, re
from urllib2 import urlopen

# helper function to retrieve url-name pairs
def nameURL(url_soup):
    try:
        objs = []
        for n_url in url_soup.findAll("a"):
            nm = n_url.findAll("span", itemprop="name")
            if nm: objs.append({ 'name' : nm[0].string, 'url' : n_url['href'] })
        return objs
    except: return []

def get_stars(soup):
    try: return nameURL(soup.find("div", itemprop="actors"))
    except: return []

def get_directors(soup):
    try: return nameURL(soup.find("div", itemprop="director"))
    except: return []

def get_writers(soup):
    try: return nameURL(soup.find("div", itemprop="creator"))
    except: return []

def get_production(soup):
    try: return nameURL((soup.find("h4", text="Production Co:")).parent)
    except: return []

def get_genres(soup):
    try:
        genres = []
        html_genre = ((soup.findAll("div", itemprop="genre"))[0])
        genre_tags = html_genre.findAll("a")
        for genre in genre_tags: 
            genres.append(genre.string)
        return genres
    except: return []

def get_budget(soup):
    try: 
        html_budget = (soup.findAll("h4", text="Budget:"))[0].parent
        return ((html_budget.text).split())[1]
    except: return ''

def get_release(soup):
    try:
        html_release = (soup.findAll("h4", text="Release Date:"))[0].parent
        return ' '.join(((html_release.text).split())[2:6])
    except: return ''

def get_tagline(soup):
    try: return (soup.find("p", itemprop="description")).string
    except: return ''

def get_castlist(soup):
    try:
        cast_html = soup.find("table", "cast_list")
        cast_tags = cast_html.findAll("span", itemprop="name")
        return map(lambda x: x.string, cast_tags)
    except: return []

def get_countries(soup):
    try:
        html_country = (soup.findAll("h4", text="Country:"))[0].parent
        return map(lambda x: x.string, html_country.findAll("a", itemprop="url"))
    except: return []

def get_metascore(soup):
    try: return (soup.find("a", title=re.compile("provided by Metacritic.com")).string).strip()
    except: return ''

def get_userscore(soup):
    try:
        score = (soup.find("span", itemprop="ratingValue")).string
        count = (soup.find("span", itemprop="ratingCount")).string
        return { 'score' : score, 'count' : count }
    except: return {}
