from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import json
from elasticsearch import Elasticsearch
from confluent_kafka import Producer
from config import conf


def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err:
        print('Message delivery failed: {}'.format(err))
    else:
        print(f"Message delivered {msg.value()} an topic {msg.topic()}")

url = "https://www.chefkoch.de/wochenrezepte/"
try:
    website_response = requests.get(url)
except requests.exceptions.HTTPError as err:
    print(f"HTTPError occured while calling {url}, error: {err}")
    print("\n exiting code!")
    exit()
html = website_response.content
fettucine_alfredo = BeautifulSoup(html, 'html.parser')
recipe_divs = fettucine_alfredo.find_all('a', class_='wr-card__link')

# get all the links from the list on the wochenrezepte page
link_list = []
for div in recipe_divs:
    mylink = div.get('href')
    link_list.append("https://www.chefkoch.de" + mylink)
# get current datetime as readAt
# get current time down to the second
now = datetime.now().replace(second=0, microsecond=0)
# transform date format to iso 8601
iso_now = now.isoformat()
# Create producer
producer = Producer(conf)

# flushing just to be sure
producer.flush()

# Grab information for each wochenrezept
articles = []
for article_link in link_list:
    # perform new request
    try:
        website_response = requests.get(article_link)
    except requests.exceptions.HTTPError as err:
        print(f"HTTPError occured while calling {article_link}, error: {err}")
    html = website_response.content
    fettucine_alfredo = BeautifulSoup(html, 'html.parser')
    title = fettucine_alfredo.find('h1').get_text()
    # shorten description
    description = fettucine_alfredo.find('p', class_='recipe-text').text
    description = description.replace(" ", "").replace("\n", "")
    # grab image link
    img_link = fettucine_alfredo.find('img', class_='i-amphtml-fill-content i-amphtml-replaced-content')['src']
    # grab published at
    publishedAt = fettucine_alfredo.find('span', class_='recipe-date rds-recipe-meta__badge').text
    # remove newlines, spaces and everything except numbers and '.' using regex
    publishedAt = publishedAt.replace(" ", "").replace("\n", "")
    publishedAt = re.sub(r"[^0-9.]", "", publishedAt)
    date_object = datetime.strptime(publishedAt, '%d.%m.%Y')
    iso_format = date_object.isoformat()


    # Bring into correct format for kafka connection, create dictionary
    article = {
        'source': {
            'id': None,
            'name': 'www.chefkoch.de'
        },
        'author': 'www.chefkoch.de',
        'title': title,
        'description': description,
        'url': article_link,
        'urlToImage': img_link,
        'publishedAt': publishedAt,
        'content': "",
        'readAt': str(iso_now),
        'category': 'rezept'
    }

    json_string = json.dumps(article)
    my_string = json_string.encode("utf-8")
    # send json info to kafka
    producer.produce("topic_0", my_string, callback=delivery_report, partition=0)
    # Wait for any outstanding messages to be delivered and delivery report
    # callbacks to be triggered.
    producer.flush()

    print('hallo')
