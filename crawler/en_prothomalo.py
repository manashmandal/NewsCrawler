# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 20:37:16 2016

@author: Manash
"""
from bs4 import BeautifulSoup
import urllib2
import unicodedata
from datetime import datetime
import time

# Header 
_header = { 'User-agent': 'Mozilla/5.0' }

# Converts 24h format into 12h format
def get_12h_time(t):
    time = datetime.strptime(t, "%H:%M")
    return time.strftime("%I:%M %p")

# Returns current time
def get_current_time():
    return time.strftime("%d-%m-%Y %H:%M", time.gmtime())

# Returns Formatted news update date
def get_update_time(unformatted_time):
    return unformatted_time.replace(unformatted_time[:5], get_12h_time(unformatted_time[:5]))

# Returns news category
def get_news_category(news_url):
    url = news_url[26:]
    cat = ''
    for letter in url:
        if letter == '/':
            return cat.capitalize()
        if letter == '-':
            return "Science & Tech"
        cat += letter
    return cat.capitalize()


def get_latest_news():
    # baseurl
    news_paper_url = "http://en.prothom-alo.com/archive"
    baseurl = 'http://en.prothom-alo.com/'

    #Adding header to avoid banning
    req = urllib2.Request(news_paper_url, headers=_header)

    # request
    prothom_alo_request = urllib2.urlopen(req)

    # Creating soup
    prothomalo_soup = BeautifulSoup(prothom_alo_request, 'lxml')


    # Getting all news links 
    news_links = [baseurl + link['href'] for link in prothomalo_soup.find('div', {'class' : 'list list_square mb20'}).findAll('a')]

    # selecting first news
    first_news = news_links[0]

    #Adding a header to avoid banning
    req2 = urllib2.Request(first_news, headers=_header)

    # Request of the first news
    news_request = urllib2.urlopen(req2)

    # soup
    first_news_soup = BeautifulSoup(news_request)

    # getting news items
    news_title = first_news_soup.title.get_text()
    news_text = unicodedata.normalize('NFKD', first_news_soup.find(itemprop="articleBody").get_text()).encode('ascii', 'ignore')
    news_update = get_update_time(first_news_soup.find(itemprop="datePublished").get_text())
    news_reporter = first_news_soup.find('span', {'class' : 'author'}).get_text()
    news_scrape_time = get_current_time()
    news_category = get_news_category(first_news)
    
    print "News title: " +  first_news_soup.title.get_text()
    print "Last Update: " + news_update
    print "Reporter: "  + news_reporter
    print "Category: " + news_category
    print "\n\n"
    print "Content: \n-----------------\n"
    print news_text
    print "--------------------------\n\n"
    print "Scrape time: " + news_scrape_time
    
if __name__ == '__main__':
    get_latest_news()