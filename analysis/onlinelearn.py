import imdb, json, math
#from textblob import TextBlob
from sklearn.svm import SVC
import matplotlib.pyplot as plt
from copy import deepcopy
from featurize import avg_float_list, MONTH_LIST
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso

data = sorted(imdb.load_json('parsed.json'), key=lambda k: k['ordinaldate'])

fields = ['stars', 'directors', 'writers', 'production']

kmap = { 'month' : MONTH_LIST,
		 'mpaa' : ['G', 'PG_13', 'R', 'PG'],
		 'genres' : imdb.load_json('genres.json') }

M100, M50 = 100000000, 50000000

def labelbinarize(data):
	imap = {}
	for i in range(len(data)): 
		imap[data[i]] = i
	return imap

def getLBMap():
	LBMap = {}
	for key in kmap.keys():
		LBMap[key] = labelbinarize(kmap[key])
	return LBMap

def getVector(kind, f_data, LBMap):
	if type(f_data) is not list:
		f_data = [f_data]
	v_lbmap = LBMap[kind]
	out = [0] * len(v_lbmap)
	for feature in f_data:
		out[v_lbmap[feature]] = 1
	return out

def discretize(x, threshold, do_it):
	if do_it:
		if x < threshold: return 0
		else: return 1
	else: return x

def vectorizeMovie(movie, LBMap, DMAP, Discrete=False, Sentiment=False):
	OUT = []

	for field in ['month', 'mpaa', 'genres']:
		OUT += getVector(field, movie[field], LBMap)

	OUT += [discretize(movie['runtime'], 90, Discrete)]
	OUT += [discretize(movie['budget'], M50, Discrete)]

	for entity in movie['stars']:
		e_name = entity['name']
		v = DMAP['stars'][e_name]
		for subfield in ['high', 'avg']:

			OUT += [discretize(v[subfield], M100, Discrete)]

	for field in ['directors', 'writers', 'production']:
		ls_vals = []
		for entity in movie[field]:
			e_name = entity['name']
			ls_vals += [DMAP[field][e_name]['avg']]
		OUT += [discretize(avg_float_list(ls_vals), M100, Discrete)]

	if Sentiment:
		tag = movie['tagline']
		if tag:
			tblob = TextBlob(tag.strip().encode('ascii', 'ignore'))
			if float(tblob.sentiment.polarity) >= 0.0: 
				OUT += [1]
			else: OUT += [0]
		else: OUT += [1]

	return OUT

def createEmpty():

	EMAP = {}

	for item in fields: EMAP[item] = {}

	for movie in data:

		for field in fields:

			for entity in movie[field]:

				e_name = entity['name']

				EMAP[field][e_name] = { 'hightime' : 0, 'high' : 0, 'avg': 0, 'N': 0 }

	return EMAP

def update(movie, DMAP):

	rev = movie['revenue']
	d_ord = movie['ordinaldate']

	for field in fields:

		for entity in movie[field]:

			e_name = entity['name']

			v = DMAP[field][e_name]

			v['avg'] = ((v['N'] * v['avg']) + rev) / float(v['N'] + 1)

			if rev > v['high']: 
				v['high'] = rev
				v['hightime'] = d_ord
			
			v['N'] += 1

	return DMAP

def traverse_movies_OLS():
	LBMAP = getLBMap()
	DMAP = createEmpty()

	P_ERRORS, ERRORS = [], []

	training_data, training_response = [], []

	for i in range(len(data)):

		movie = data[i]
		m_rev = movie['revenue']

		myvector = vectorizeMovie(movie, LBMAP, DMAP)

		if i > 100:
			model = LinearRegression()
			model.fit(training_data, training_response)
			raw = math.fabs(model.predict(myvector) - m_rev)
			ERRORS.append(raw)
			P_ERRORS.append(round(raw/m_rev, 4))
		
		training_data.append(myvector)
		training_response.append(m_rev)

		DMAP = update(movie, DMAP)

	print 'all', avg_float_list(P_ERRORS)
	print 'all', avg_float_list(ERRORS)
	print 'all', avg_float_list(ERRORS[3200:])

#traverse_movies_OLS()

def traverse_movies_ridge():
	LBMAP = getLBMap()
	DMAP = createEmpty()

	P_ERRORS, ERRORS = [], []

	training_data, training_response = [], []

	for i in range(len(data)):

		movie = data[i]
		m_rev = movie['revenue']

		myvector = vectorizeMovie(movie, LBMAP, DMAP)

		if i > 100:
			model = Ridge(alpha = .5)
			model.fit(training_data, training_response)
			raw = math.fabs(model.predict(myvector) - m_rev)
			ERRORS.append(raw)
			#P_ERRORS.append(round(raw/m_rev, 4))
		
		training_data.append(myvector)
		training_response.append(m_rev)

		DMAP = update(movie, DMAP)

	#print 'all', avg_float_list(P_ERRORS)
	print 'all', avg_float_list(ERRORS)
	#print 'all', avg_float_list(ERRORS[3200:])

def traverse_movies_lasso():
	LBMAP = getLBMap()
	DMAP = createEmpty()

	P_ERRORS, ERRORS = [], []

	training_data, training_response = [], []

	for i in range(len(data)):

		movie = data[i]
		m_rev = movie['revenue']

		myvector = vectorizeMovie(movie, LBMAP, DMAP)

		if i > 3695:
			model = Lasso(alpha = .05)
			model.fit(training_data, training_response)
			raw = math.fabs(model.predict(myvector) - m_rev)
			ERRORS.append(raw)
			#P_ERRORS.append(round(raw/m_rev, 4))
		
		training_data.append(myvector)
		training_response.append(m_rev)

		DMAP = update(movie, DMAP)

	#print 'all', avg_float_list(P_ERRORS)
	print 'all', avg_float_list(ERRORS)
	#print 'all', avg_float_list(ERRORS[3200:])

#print "RIDGE TIME"
#traverse_movies_ridge()
#print "LASSO TIME"
#traverse_movies_lasso()

def traverse_movies_classify():

	results_map = {}
	# modeltypes = [ BernoulliNB(), LogisticRegression(), 
	#			   RandomForestClassifier(), SVC() ]

	modeltypes = [ BernoulliNB() ]
    
	for mt in modeltypes:
		results_map[str(mt)] = { 0: [], 1: [] }

	for mt in modeltypes:

		total = { 0 : 0, 1 : 0 }
		correct = { 0 : 0, 1 : 0 }
		LBMAP, DMAP = getLBMap(), createEmpty()

		X, Y = [], []

		for i in range(len(data)):

			movie = data[i]
			m_rev = discretize(movie['revenue'], M100, True)

			myvector = vectorizeMovie(movie, LBMAP, DMAP, Discrete=True)

			if i > 100:

				model = deepcopy(mt)
				model.fit(X, Y)

				prediction = model.predict(myvector)

				if prediction == m_rev: 
					correct[m_rev] += 1
				total[m_rev] += 1

				for j in [0, 1]:

					if total[j] > 0:

						val = correct[j] / float(total[j])

						results_map[str(mt)][j].append(val)

					else:

						results_map[str(mt)][j].append(val)

				if (i % 1000) == 0:
					print (i/float(len(data))), str(mt)[:11]

			Y.append(m_rev)
			X.append(myvector)
			DMAP = update(movie, DMAP)

		print str(mt)
		print 'total', total
		print 'correct', correct


	# imdb.save_json(results_map, 'classify_results.json')

	"""
	for mt in modeltypes:
		for cls in [0,1]:
			scores = results_map[str(mt)][cls]
			plt.plot(range(len(scores)), scores, label=('class label' + str(cls)))
	plt.legend()
	plt.show()
	"""

def make_nice_graph(cls):

	gdata = imdb.load_json('classify_results.json')

	for key in gdata.keys():
		model = key.split('(')[0]
		scores = gdata[key][cls]
		plt.plot(range(len(scores)), scores, label=model, linewidth=2)

	if '0' in cls:
		title = '< 100M Revenue (Class Label 0)'
	else: title = '100M+ Revenue (Class Label 1)'
	plt.legend()
	plt.suptitle(title)
	plt.xlabel('Time Step')
	plt.ylabel('Classification Accuracy')
	plt.show()

def graph_regression():

	results = { 'Overall' : [0, 0, []],
				'All Correct' : [0, 0, []],
				'<100M Correct' : [0, 0, []],
				'100M+ Correct' : [0, 0, []] }

	with open('combined.csv', 'r') as f:

		for line in f:

			vals = line.split(',')
			true, pred, err = vals[0], vals[1], float(vals[2])

			all_c, c0_c, c1_c = False, False, False

			if true == pred:
				all_c = True

				if true == '1':
					c1_c = True
				else: c0_c = True

			for key in results.keys():

				if ((key == 'Overall') or (key == 'All Correct' and all_c) 
					or (key == '<100M Correct' and c0_c) or (key == '100M+ Correct' and c1_c)):

					n, ravg = results[key][0], results[key][1]

					new_avg = ((n * ravg) + err) / float(n+1)

					results[key][0], results[key][1] = (n + 1), new_avg

					results[key][2] += [new_avg]

				else:

					results[key][0] += 1
					results[key][2] += [results[key][1]]

	for key in ['Overall', 'All Correct', '<100M Correct', '100M+ Correct']:
		model, scores = key, results[key][2]
		print model, avg_float_list(scores)
		plt.plot(range(len(scores)), scores, label=model, linewidth=2)


	plt.legend()
	plt.suptitle('Regression Performance on Correct Classifications')
	plt.xlabel('Time Step')
	plt.ylabel('Mean Absolute Error')
	plt.ylim(10000000, 60000000)
	plt.show()


def traverse_movies_grad():

	LBMAP, DMAP = getLBMap(), createEmpty()
	training_data, training_response = [], []

	for i in range(len(data)):
		movie = data[i]
        m_rev = movie['revenue']
        myvector = vectorizeMovie(movie, LBMAP, DMAP)
        if i == 1000:
            model = LinearRegression()
            model.fit(training_data, training_response)
            coefficients = model.coef_
            intercept = model.intercept_
            coef_list = []
            for item in coefficients:
                coef_list.append(item)
        elif i > 1000:
            l_rate = 1/float(i)
            prediction = 0
            for j in range(len(coef_list)):
                prediction += coef_list[j]*myvector[j]
            prediction += intercept
            
            print math.fabs(prediction-m_rev)
            
            norm = 0
            for k in range(len(myvector)):
                norm += myvector[k]
            
            gradient = m_rev - prediction #direction matters
            
            for j in range(len(coef_list)):
                coef_list[j] += l_rate*gradient*myvector[j]/(norm)
            intercept += l_rate*gradient
            
        training_data.append(myvector)
        training_response.append(m_rev)

#traverse_movies_grad()

#traverse_movies_classify()
#make_nice_graph('0')
#make_nice_graph('1')

graph_regression()
