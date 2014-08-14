"""
Functions to vectorize movie profiles and split into test / train sets
"""

import imdb, json
from copy import deepcopy
from numpy import median

E_FIELDS = ['directors', 'writers', 'production']

MONTH_LIST = [ 'January', 'February', 'March', 'April', 
               'May', 'June', 'July', 'August', 
               'September', 'October', 'November', 'December' ]

DELETE_THESE = ['castlist', 'countries', 'genres', 'link', 'month', 
			 	'mpaa', 'release', 'stars', 'tagline', 'userscore']

# return the average of a list of floats
def avg_float_list(float_list):
	if len(float_list) > 0:
		return round(sum(float_list) / float(len(float_list)), 2)
	else: return 0.0

# get list of entities associated with a movie
def get_entity_list(movie):
	fields, e_list = ['stars', 'directors', 'writers', 'production'], []
	for field in fields:
		f_list = movie[field]
		for entity in f_list: 
			e_list.append(entity['name'])
	return e_list

# create a mapping of unique entities to associated movies
def entity_movie_map(movielist):
	EMM = {}
	for movie in movielist:
		m_name = movie['name']
		entity_list = get_entity_list(movie)
		for entity in entity_list:
			if entity in EMM:
				if m_name in EMM[entity]: 
					continue
				else: 
					EMM[entity].append(m_name)
			else: EMM[entity] = [m_name]
	return EMM

# create a mapping of unique entities to average revenue of movies
# associated with the unique entity
def entity_revenue_map(EMM, MDM):

	ERM2009 = {}
	def compute_entity_avg(entity):
		e_movies, e_revenues = EMM[entity], []
		for e_m in e_movies:
			e_revenues.append(MDM[e_m]['revenue'])
		return avg_float_list(e_revenues)

	for entity in EMM.keys():
		ERM2009[entity] = compute_entity_avg(entity)

	return ERM2009

# create a mapping of movie name to movie data
def movie_data_map(movielist):
	MDM = {}
	nonfield = [ 'castlist', 'countries',  'genres', 'link', 'month', 
				 'mpaa', 'release', 'tagline', 'writers' ]

	for movie in movielist:
		m_name = movie['name']

		for nf in nonfield: del movie[nf]

		if m_name in MDM:
			print 'duplicate', m_name
		else: MDM[m_name] = movie
	return MDM

def zero_dict_from_list(features):
    out = {}
    for feature in features: out[feature] = 0
    return out

def generate_zero_dict_map():
    return { 'genres' : zero_dict_from_list(imdb.load_json('genres.json')),
             'month' : zero_dict_from_list(MONTH_LIST),
             'mpaa' : zero_dict_from_list(['G', 'PG_13', 'R', 'PG']) }

def featurize():
	zero_dict_map = generate_zero_dict_map()

	full_data = imdb.load_json('parsed.json')
	train = filter(lambda x: (x['year'] < 2009), full_data)
	test = filter(lambda x: (x['year'] >= 2009), full_data)

	ERM2009 = imdb.load_json('ERM2009.json')

	ERM_AVG = median(list((zip(*ERM2009.items()))[1]))
	print 'ERM_MED', ERM_AVG

	def dvectorize(kind, data):
		zdict = deepcopy(zero_dict_map[kind])
		if type(data) is not list: data = [data]
		for feature in data:
			if feature in zdict: zdict[feature] = 1
		return zdict

	def apply_featurization(movie):

		for case in ['genres', 'mpaa', 'month']:
			case_dict = dvectorize(case, movie[case])
			for key in case_dict.keys(): 
				movie[key] = case_dict[key]

		for j in range(len(movie['stars'])):
			actor_name = movie['stars'][j]['name']
			if actor_name in ERM2009:
				movie['actor'+str(j)] = ERM2009[actor_name]
			else: movie['actor'+str(j)] = ERM_AVG

		for e_field in E_FIELDS:
			VALS = []
			for entity in movie[e_field]:
				if entity['name'] in ERM2009:
					VALS.append(ERM2009[entity['name']])
				else: VALS.append(ERM_AVG)

			movie[e_field] = avg_float_list(VALS)

		for thing in DELETE_THESE: del movie[thing]

		return movie

	featurized_train = map(apply_featurization, train)
	featurized_test = map(apply_featurization, test)

	with open('featurized4_train.json', 'w') as f:
		json.dump(featurized_train, f, sort_keys = True, indent = 4)

	with open('featurized4_test.json', 'w') as f:
		json.dump(featurized_test, f, sort_keys = True, indent = 4)
