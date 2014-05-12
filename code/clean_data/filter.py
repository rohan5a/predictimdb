import json, imdb
from datetime import date

MONTH_LIST = [ 'January', 'February', 'March', 'April', 
               'May', 'June', 'July', 'August', 
               'September', 'October', 'November', 'December' ]

def numericize(s):
    return filter(lambda x: x in '0123456789', s)

def get_inflation_data():
    deflators = {}
    with open("deflators.txt", 'r') as f:
        str_data = f.read()
        lines = str_data.split('\r')
        for line in lines:
            year = int(line[0:4])
            deflator = float(line[5:])
            deflators.update({ year : deflator })
    return deflators

def my_filter(movie):
    # get rid of movies that don't have budget, runtime
    # 3 star actors, or rating and that aren't documentaries or old
    bad_ratings = ['TV_PG', 'UNRATED', 'NOT_RATED', 
    'TV_MA', '' , 'NC_17', 'TV_14', 'APPROVED']
    has_budget, has_runtime, has_stars = True, True, True
    is_doc, is_old, is_rated = False, False, True

    for genre in movie['genres']:
        if "Documentary" in genre: is_doc = True
    
    if movie['year'] < 1984: is_old = True

    if movie['mpaa'] in bad_ratings: is_rated = False

    if not numericize(movie['budget']): has_budget = False
                
    if not numericize(movie['runtime']): has_runtime = False

    if len(movie['stars']) < 3: has_stars = False

    valid = (not is_doc) and (not is_old) and is_rated

    if valid and has_budget and has_runtime and has_stars:
        return True
    else: return False

def filter_data():

    data = imdb.load_json('master.json')
    newdata = sorted(data, key=lambda k: k['year'])
    newdata.pop() # get rid of last movie with no fields

    def assign_year(movie): # parse string year
        year = int(str(movie['year'][1:5]))
        movie['year'] = year # process year field
        return movie

    filtered = sorted(filter(my_filter, map(assign_year, newdata)), key=lambda k: k['year'])
    print 'filtered length of %d' % len(filtered)
    return filtered

def parse_data():

    M_NAMES = []
    filtered_data = filter_data()
    deflators = get_inflation_data()

    def adjust(num_val, year_val): # inflation adjustment
        return round((num_val*(100.0/deflators[year_val])), 2)

    def parse_rev(sr):
        if 'M' in sr: factor = 1000000
        elif 'K' in sr: factor = 1000
        sr = sr.replace('$', '')
        return (float(sr[:-1]) * factor)

    def parse_meta(s):
        if s and '/' in s:
            vals = s.split('/')
            return int(vals[0])
        else: return 0

    def parse_date(s):

        def month_code(m):
            if m in MONTH_LIST:
                return (MONTH_LIST.index(m) + 1)
            else: return 0

        def year_pos(ls):
            for k in range(len(ls)):
                if len(ls[k]) == 4 and ls[k].isdigit(): return k

        lss = s.split()
        r_ls = lss[:year_pos(lss)+1]

        if len(r_ls) == 1:
            d_obj = date(int(r_ls[0]), 1, 1)
        elif len(r_ls) == 2:
            d_obj = date(int(r_ls[1]), month_code(r_ls[0]), 1)
        elif len(r_ls) == 3:
            d_obj = date(int(r_ls[2]), month_code(r_ls[1]), int(r_ls[0]))
        else: 
            print 'error on %s' %s
            return None

        return (MONTH_LIST[d_obj.month - 1], d_obj.toordinal())

    def parse_fields(movie):

        if movie['name'] in M_NAMES: movie['name'] = ' '.join([movie['name'], '(new)'])
        else: M_NAMES.append(movie['name'])

        movie['revenue'] = adjust(parse_rev(movie['revenue']), movie['year'])

        movie['metascore'] = parse_meta(movie['metascore'])

        movie['runtime'] = int(numericize(movie['runtime']))

        movie['budget'] = adjust(float(numericize(movie['budget'])), movie['year'])

        d_month, d_ordinal = parse_date(movie['release'])
        movie['month'], movie['ordinaldate'] = d_month, d_ordinal

        movie['genres'] = map(lambda s: (s.strip()).replace('-', ''), movie['genres'])

        # movie['ROI'] = round((movie['revenue'] / movie['budget']), 3)

        return movie

    parsed_data = map(parse_fields, filtered_data)
    print len(parsed_data)

    with open('parsed.json', 'w') as f:
        json.dump(parsed_data, f, sort_keys = True, indent = 4)

