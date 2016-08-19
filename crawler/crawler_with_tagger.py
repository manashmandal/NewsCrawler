# TODO
# StanfordNERTagger to tag the words

from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.chunk import conlltags2tree
from nltk.tree import Tree
from newspaper import Article

from bs4 import BeautifulSoup
import urllib2
import unicodedata
from datetime import datetime
import time

stanford_classifier = 'D:\StanfordParser\stanford-ner-2015-12-09\classifiers\english.all.3class.distsim.crf.ser.gz'
stanford_classifier2 = 'D:\StanfordParser\stanford-ner-2015-12-09\classifiers\english.muc.7class.distsim.crf.ser.gz'
stanford_ner_path = 'D:\StanfordParser\stanford-ner-2015-12-09\stanford-ner.jar'

st = StanfordNERTagger(stanford_classifier2, stanford_ner_path, encoding='utf-8')
st2 = StanfordNERTagger(stanford_classifier, stanford_ner_path, encoding='utf-8')


def stanfordNE2BIO(tagged_sent):
	bio_tagged_sent = []
	prev_tag = "O"
	for token, tag in tagged_sent:
		if tag == "O": #O
			bio_tagged_sent.append((token, tag))
			prev_tag = tag
			continue
		if tag != "O" and prev_tag == "O": # Begin NE
			bio_tagged_sent.append((token, "B-"+tag))
			prev_tag = tag
		elif prev_tag != "O" and prev_tag == tag: # Inside NE
			bio_tagged_sent.append((token, "I-"+tag))
			prev_tag = tag
		elif prev_tag != "O" and prev_tag != tag: # Adjacent NE
			bio_tagged_sent.append((token, "B-"+tag))
			prev_tag = tag

	return bio_tagged_sent

def stanfordNE2tree(ne_tagged_sent):
	bio_tagged_sent = stanfordNE2BIO(ne_tagged_sent)
	sent_tokens, sent_ne_tags = zip(*bio_tagged_sent)
	sent_pos_tags = [pos for token, pos in pos_tag(sent_tokens)]

	sent_conlltags = [(token, pos, ne) for token, pos, ne in zip(sent_tokens, sent_pos_tags, sent_ne_tags)]
	ne_tree = conlltags2tree(sent_conlltags)
	return ne_tree

def create_ner_entities_tuple(text):
	ne_tagged_sent = st.tag(text.split())
	ne_tree = stanfordNE2tree(ne_tagged_sent)
	ne_in_sent = []
	for subtree in ne_tree:
		if type(subtree) == Tree: # If subtree is a noun chunk, i.e. NE != "O"
			ne_label = subtree.label()
			ne_string = " ".join([token for token, pos in subtree.leaves()])
			ne_in_sent.append((ne_string, ne_label))
	return ne_in_sent



def create_ner_entities_tuple_2(text):
    ne_tagged_sent = st2.tag(text.split())
    ne_tree = stanfordNE2tree(ne_tagged_sent)
    ne_in_sent = []
    for subtree in ne_tree:
    	if type(subtree) == Tree: # If subtree is a noun chunk, i.e. NE != "O"
    		ne_label = subtree.label()
    		ne_string = " ".join([token for token, pos in subtree.leaves()])
    		ne_in_sent.append((ne_string, ne_label))
    return ne_in_sent





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

    return news_text


news_text = "Nearly 7,000 imported Infiniti and Nissan Fuga automobiles will be recalled from China, the countrys quality watchdog said on Tuesday. According to the General Administration of Quality Supervision, Inspection and Quarantine, the 6,961 recalled autos were installed with problematic gas generators, Xinhua news agency reported. Global and Chinese automakers recalled a record 8.8 million 100% defective vehicles in the first half of 2016, more than double the number for the same period last year. Japanese automakers recalled the largest number of vehicles at nearly 5.7 million units in 40 batches, followed by the US and German automakers. My name is Manash and it is 100% accurate."


news_text = "While in France, Christine Lagarde discussed 100% short-term stimulus efforts in a recent interview with the Wall Street Journal."

# Sums up discrete tags
def entity_group(text):
    # Getting rid of tokens with Object Tag
    tokenized_words = [token for token in st.tag(word_tokenize(text)) if token[1] != 'O']

    comparator = tokenized_words[0]
    list_index = 0
    append_index = 0

    # Store the element from the beginning of the list
    comparator = tokenized_words[0]

    # Insert first element to the tag_touple list
    tag_touple_list = [(comparator[0], comparator[1])]

    # Increase the list index since we've added an element at the beginning
    list_index += 1

    # Continue iteration until the index has reached to the end of the list
    while (list_index < len(tokenized_words)):

        if (comparator[1] == tokenized_words[list_index][1]):

            # If it's a Percentage symbol skip the space
            space_or_not = '' if tokenized_words[list_index][0] == '%' else ' '

            # Get the previous element then append it with the new one
            to_be_appended = comparator[0] + space_or_not + tokenized_words[list_index][0]

            # Set the modified value to the touple list
            tag_touple_list[append_index] = (to_be_appended, comparator[1])

            # Increase list index
            list_index += 1

        else:
            # Replace the comparator with new one
            comparator = tokenized_words[list_index]

            # Place the comparator to the list
            tag_touple_list.append((comparator[0], comparator[1]))

            # Increase index
            list_index += 1

            # Since it's a new entity we need to increase the location of the insertion
            append_index += 1



    print tag_touple_list




if __name__ == '__main__':
    news_ner_tags = {}
    ner_person = []
    ner_location = []
    ner_organization = []
    ner_date = []
    ner_money = []
    ner_percent = []
    ner_time = []


    entity_group(news_text)
