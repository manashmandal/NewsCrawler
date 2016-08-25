# Author: Manash
# This piece of code collects names from http://www.babynamesdirect.com
# Version: 0.01v
# TODO: i) Add automatic scraping capability
# 	ii) Get all available page links


from bs4 import BeautifulSoup
import urllib2

# Taking this url as baseurl
url = 'http://www.babynamesdirect.com/bengali-baby-names/Boy/A'

# Requesting the page
request = urllib2.Request(url)

page = urllib2.urlopen(request)

page_soup = BeautifulSoup(page, 'lxml')

name_table = page_soup.find('table', attrs={'class': 'tbl bnames boy'})

name_table_body = name_table.find('tbody')

rows = name_table_body.find_all('tr')

table_rows = []

for row in rows:
	attribute = row.attrs.get('class')
	if attribute is None:
		cols = row.find_all('td')
		cols = [ele.text.strip() for ele in cols]
		# Checking empty items
		table_rows.append([ele for ele in cols if ele])


# Print out the collected names
for name in table_rows:
	print name[1]
