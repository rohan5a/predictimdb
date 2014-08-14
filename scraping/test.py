from imdb import scrape_movie_page, scrape_links

def test_page_scraper():
	# test 'Hancock', 'No Country for Old Men' and 'Girl W/ Dragon Tattoo'
	urls = ['/title/tt0448157/', '/title/tt0477348/', '/title/tt1132620/']
	map(scrape_movie_page, urls)

def test_link_crawler():
	scrape_links()

test_link_crawler()

