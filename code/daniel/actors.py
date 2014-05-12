import json
from pprint import pprint

stars, actors, directors, writers, studios, deflators = {}, {}, {}, {}, {}, {}

with open("deflators.txt", 'r') as f:
    str_data = f.read()
    lines = f.split('\r')
    for line in lines:
        year = int(line[0:4])
        deflator = float(line[5:])
        deflators.update({year:deflator})

data = []
for i in range(0, 70):
    file_name = 'movies{0} - {1}.json'.format(i*100, (i+1)*100)
    with open(file_name) as json_data:
        d = json.load(json_data)
        json_data.close()
        data = data + d
        
newdata = sorted(data, key=lambda k: k['year'])
newdata.pop()

filt_data = []
bad_ratings = ['TV_PG', 'UNRATED', 'NOT_RATED', 'TV_MA', '' , 'NC_17', 'TV_14', 'APPROVED']
is_doc = False
is_old = False
is_rated = True
for movie in newdata:
    is_doc = False
    is_old = False
    is_rated = True
    for type in movie['genres']:
        if type == " Documentary":
            is_doc = True
    year = int(str(movie['year'][1:5]))
    movie['year'] = year
    if year < 1984:
        is_old = True
    for item in bad_ratings:
        if movie['mpaa'] == item:
            is_rated = False
    if not is_doc and not is_old and is_rated:
        rev = float(movie['revenue'][1:-1])
        mult = movie['revenue'][-1:]
        if mult == 'M':
            rev = rev*(1000000)
        elif mult == 'K':
            rev = rev*(1000)
        defl = deflators[movie['year']]
        rev = rev*(100.0/defl)
        movie['revenue'] = rev
        filt_data.append(movie)

#filt_data has removed movies from before 1975; removed movies w/dumb mpaa ratings;
#removed documentaries; and has deflated the revenue wrt inflation; and made rev and year into floats

filt_data = sorted(filt_data, key=lambda k: k['year'])
print len(filt_data)

with open('non_docs.json', 'w') as outfile:
    json.dump(filt_data, outfile, sort_keys = True, indent = 4)

"""training = newdata[:6033]
testing = newdata[6033:]
with open('training.json', 'w') as outfile:
     json.dump(training, outfile, sort_keys = True, indent = 4)
with open('testing.json', 'w') as outfile:
     json.dump(testing, outfile, sort_keys = True, indent = 4)

for movie in training:
    for actor in movie['stars']:
        name = actor['name']
        if stars.has_key(name):
            stars[name].update({movie['name']:[movie['revenue'], movie['release']]})
        else:
            stars.update({name:{}})
            stars[name].update({movie['name']:[movie['revenue'], movie['release']]})
        
    for director in movie['directors']:
        name = director['name']
        if directors.has_key(name):
            directors[name].update({movie['name']:[movie['revenue'], movie['release']]})
        else:
            directors.update({name:{}})
            directors[name].update({movie['name']:[movie['revenue'], movie['release']]})
        
    for writer in movie['writers']:
        name = writer['name']
        if writers.has_key(name):
            writers[name].update({movie['name']:[movie['revenue'], movie['release']]})
        else:
            writers.update({name:{}})
            writers[name].update({movie['name']:[movie['revenue'], movie['release']]})
        
    for studio in movie['production']:
        name = studio['name']
        if studios.has_key(name):
            studios[name].update({movie['name']:[movie['revenue'], movie['release']]})
        else:
            studios.update({name:{}})
            studios[name].update({movie['name']:[movie['revenue'], movie['release']]})
        
    for actor in movie['castlist']:
        name = actor
        if actors.has_key(name):
            actors[name].update({movie['name']:[movie['revenue'], movie['release']]})
        else:
            actors.update({name:{}})
            actors[name].update({movie['name']:[movie['revenue'], movie['release']]})

with open('stars.json', 'w') as outfile:
     json.dump(stars, outfile, sort_keys = True, indent = 4)
     
with open('actors.json', 'w') as outfile:
     json.dump(actors, outfile, sort_keys = True, indent = 4)

with open('directors.json', 'w') as outfile:
     json.dump(directors, outfile, sort_keys = True, indent = 4)

with open('writers.json', 'w') as outfile:
     json.dump(writers, outfile, sort_keys = True, indent = 4)

with open('studios.json', 'w') as outfile:
     json.dump(studios, outfile, sort_keys = True, indent = 4)
     
Now we need to make a big JSON, a list of dictionaries. Each dictionary is a movie, 
each movie has indicators for each possible maturity rating and each possible genre; and
 has an entry for each category stars/directors/writers/studios which is the total average 
 of the revenues for every movie done by all the entries in that category"""