from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.chunk import conlltags2tree
from nltk.tree import Tree
from newspaper import Article

# indico API for sentiment analysis
import indicoio

from NewsCrawler.credentials_and_configs.keys import INDICOIO_API_KEY


class Tagger:

    def __init__(self, classifier_path, ner_path):
        self.LOCATION = []
        self.PERSON = []
        self.ORGANIZATION = []
        self.TIME = []
        self.MONEY = []
        self.PERCENT = []

        self.LIST_LOCATION = []
        self.LIST_PERSON = []
        self.LIST_ORGANIZATION = []
        self.LIST_TIME = []
        self.LIST_MONEY = []
        self.LIST_PERCENT = []

        indicoio.config.api_key = INDICOIO_API_KEY

        self.classifier_path = classifier_path
        self.ner_path = ner_path

        # StanfordNERTagger Object
        self.st = StanfordNERTagger(
            classifier_path, ner_path, encoding='utf-8')

    def stanfordNE2BIO(self, tagged_sent):
        bio_tagged_sent = []
        prev_tag = "O"
        for token, tag in tagged_sent:
            if tag == "O":  # O
                bio_tagged_sent.append((token, tag))
                prev_tag = tag
                continue
            if tag != "O" and prev_tag == "O":  # Begin NE
                bio_tagged_sent.append((token, "B-" + tag))
                prev_tag = tag
            elif prev_tag != "O" and prev_tag == tag:  # Inside NE
                bio_tagged_sent.append((token, "I-" + tag))
                prev_tag = tag
            elif prev_tag != "O" and prev_tag != tag:  # Adjacent NE
                bio_tagged_sent.append((token, "B-" + tag))
                prev_tag = tag

        return bio_tagged_sent

    def stanfordNE2tree(self, ne_tagged_sent):
        bio_tagged_sent = stanfordNE2BIO(ne_tagged_sent)
        sent_tokens, sent_ne_tags = zip(*bio_tagged_sent)
        sent_pos_tags = [pos for token, pos in pos_tag(sent_tokens)]
        sent_conlltags = [(token, pos, ne) for token, pos, ne in zip(
            sent_tokens, sent_pos_tags, sent_ne_tags)]
        ne_tree = conlltags2tree(sent_conlltags)
        return ne_tree

    def create_ner_entities_tuple(self, text):
        ne_tagged_sent = st.tag(text.split())
        ne_tree = stanfordNE2tree(ne_tagged_sent)
        ne_in_sent = []
        for subtree in ne_tree:
            if type(subtree) == Tree:  # If subtree is a noun chunk, i.e. NE != "O"
                ne_label = subtree.label()
                ne_string = " ".join(
                    [token for token, pos in subtree.leaves()])
                ne_in_sent.append((ne_string, ne_label))
        return ne_in_sent

    def entity_group(self, text):
        # Tokenizing the news content
        tokenized_words = self.st.tag(word_tokenize(text))
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
                space_or_not = '' if tokenized_words[
                    list_index][0] == '%' else ' '
                # which is to be appended
                to_be_appended = tag_touple_list[append_index][
                    0] + space_or_not + tokenized_words[list_index][0]
                # Set the modified value to the touple list
                tag_touple_list[append_index] = (to_be_appended, comparator[1])
                # Increase list index
                list_index += 1
                continue
            else:
                # Replace the comparator with new one
                comparator = tokenized_words[list_index]
                # print "Comparator got changed: {0}".format(comparator)
                # Place the comparator to the list
                tag_touple_list.append((comparator[0], comparator[1]))
                # Increase index
                list_index += 1
                # Since it's a new entity we need to increase the location of
                # the insertion
                append_index += 1
                # return set(tag_touple_list)
        # Getting rid of object entities
        tag_touple_list = [toup for toup in tag_touple_list if toup[1] != 'O']

        self.LOCATION = []
        self.PERSON = []
        self.ORGANIZATION = []
        self.TIME = []
        self.PERCENT = []
        self.MONEY = []

        self.LIST_LOCATION = []
        self.LIST_PERSON = []
        self.LIST_ORGANIZATION = []
        self.LIST_TIME = []
        self.LIST_MONEY = []
        self.LIST_PERCENT = []

        for tags in tag_touple_list:
            if tags[1] == 'PERSON':
                self.PERSON.append(tags[0])
                self.LIST_PERSON.append(tags[0])
            elif tags[1] == 'LOCATION':
                self.LOCATION.append(tags[0])
                self.LIST_LOCATION.append(tags[0])
            elif tags[1] == 'ORGANIZATION':
                self.ORGANIZATION.append(tags[0])
                self.LIST_ORGANIZATION.append(tags[0])
            elif tags[1] == 'PERCENT':
                self.PERCENT.append(tags[0])
                self.LIST_PERCENT.append(tags[0])
            elif tags[1] == 'TIME':
                self.TIME.append(tags[0])
                self.LIST_TIME.append(tags[0])
            elif tags[1] == 'MONEY':
                self.MONEY.append(tags[0])
                self.LIST_MONEY.append(tags[0])

        self.ORGANIZATION = list(set(self.ORGANIZATION))
        self.PERSON = list(set(self.PERSON))
        self.PERCENT = list(set(self.PERCENT))
        self.MONEY = list(set(self.MONEY))
        self.TIME = list(set(self.TIME))
        self.LOCATION = list(set(self.LOCATION))

        return tag_touple_list

    # Cleans up unnecessary symbols
    def clean_up(self, tag_touple_list):
        return self.custom_clean_up(tag_touple_list, " ) ", " ")

    # Custom clean up function
    def custom_clean_up(self, tag_touple_list, to_be_replaced, replace_with):
        for index, toup in enumerate(tag_touple_list):
            if to_be_replaced in toup[0]:
                tag_touple_list[index] = (toup[0].replace(
                    to_be_replaced, replace_with), toup[1])
        return tag_touple_list

    def get_indico_sentiment(self, text):
        ## For now we are not using up API limit
        ## We will go through the sentiments as soon as
        ## the crawl is completed
        #sentiment = indicoio.sentiment_hq(text)
        return None#sentiment
