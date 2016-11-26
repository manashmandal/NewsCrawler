# Bangladeshi Online Newspaper Crawler

## Currently working on:

* [~~en.prothom-alo.com~~](http://en.prothom-alo.com)
* [~~thedailystar.net~~](http://www.thedailystar.net)
* [dhakatribune.com](http://archive.dhakatribune.com/archive)

# Requirements

* Python 2k
* Check `requirements.txt` file to find out about the dependencies

# How to 

## 1. Installing the dependencies

Clone the repository, then at the root of the directory of the repo, open a command window/terminal and run this following command. Make sure you have `pip`.

```
pip install -r requirements.txt
```

## 2. Configuring API and StanfordNER Path

##[TODO]


## 3. Running the spiders

Open a command window /terminal at the root of the folder. Run the following commands to start scraping.

### 4. Crawling Instructions

## Spider Names

* The Daily Star -> `dailystar`
* Prothom Alo -> `prothomalo`

#### Crawl 'em all

**For Daily Star**
```
scrapy crawl dailystar
```

**For Prothom Alo**
```
scrapy crawl prothomalo
```

#### Crawling bounded by date time 

If I want to scrape all of the news between `1st January 2016` and `1st February 2016` my command will look like this, 

**Daily Star**
```
scrapy crawl dailystar -a start_date="01-01-2016" -a  end_date="01-02-2016"
```

**Prothom Alo**
```
scrapy crawl prothomalo -a start_date="01-01-2016" -a  end_date="01-02-2016"
```

#### Crawling with CSV/JSON output 

If you want to collect all crawled data in a csv or a json file you can run this command.

**Daily Star [`csv` output]**
```
scrapy crawl dailystar -a start_date="01-01-2016" -a end_date="01-02-2016" -o output_file_name.csv
```

**Daily Star [`json` output]**
```
scrapy crawl dailystar -a start_date="01-01-2016" -a end_date="01-02-2016" -o output_file_name.json
```

**Prothom Alo [`csv` output]**
```
scrapy crawl prothomalo -a start_date="01-01-2016" -a end_date="01-02-2016" -o output_file_name.csv
```

**Daily Star [`csv` output]**
```
scrapy crawl prothomalo -a start_date="01-01-2016" -a end_date="01-02-2016" -o output_file_name.json
```

## 5. Data insertion into Elasticsearch and Kibana Visualization Instructions

### [TODO]