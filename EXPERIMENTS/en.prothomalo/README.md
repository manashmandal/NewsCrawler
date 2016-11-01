# English Prothom Alo Scraper

## Requirements

* Python 2.7
* [Scrapy](https://scrapy.org/)

## How to?

Download the repository, browse the `NewsCrawler/EXPERIMENTS/en.prothomalo` folder and then open a command window (for windows) or terminal (for linux) at this location.

Then apply the following command to get the output as csv file 

`scrapy crawl prothomalo-bangladesh -o data.csv -t csv`

![image](http://i.imgur.com/qScTmMQ.gif)

# A better approach

## Run the Generalized Crawler

```
scrapy crawl prothomalo -a category=international -o international_news.csv -t csv
```

Change the parameter value of `category` for getting category wise news. 

![image](http://i.imgur.com/WVpqTE9.png)

To collect news which are tagged by `economoy` keyword, use the following command

```
scrapy crawl prothomalo -a category=economy -o economy_news.csv -t csv
```


## Result

A `data.csv` file should be created instantly and you can view the results after terminating the program. [Here is a sample of the output.](https://github.com/manashmndl/NewsCrawler/blob/master/EXPERIMENTS/en.prothomalo/Sample_Data/data.csv)


