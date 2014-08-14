import glob, imdb

master = []

files = glob.glob("data/*")

for file in files:
    m = imdb.load_movies(file)
    master.extend(m)
    print file

print len(master)

imdb.save_movies(master, 'master.json')


