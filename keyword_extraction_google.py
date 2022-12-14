import requests
from datetime import datetime


"""
Call the Elasticsearch endpoint, 
check wether or not a document already has keywords, 
if not add them and rewrite into elastic, 
stop when an entry has already been modified with keywords
Grab multiples instead of just one 
"""

import requests
import json
# Import the Elasticsearch client
from elasticsearch import Elasticsearch

def extract_keywords(text):
    # Set the API key for the Google Natural Language Processing API
    api_key = 'AIzaSyCRHHSb8Mqw22QlcILOoWwypjHs2FqBrR0'
    # Set the text to analyze

    # Set the API endpoint URL
    api_url = 'https://language.googleapis.com/v1/documents:analyzeEntities?key=' + api_key

    # Set the request payload
    payload = {
      'document': {
        'type': 'PLAIN_TEXT',
        'content': text
      },
      'encodingType': 'UTF8'
    }

    # Make the request to the API
    response = requests.post(api_url, json=payload)

    # Parse the response dictionary
    response_dict = response.json()

    # Get the list of entities from the response
    entities = response_dict['entities']

    # make sure that its not more than 10 and sort by salience, highest salience first
    top_entities = [entity for entity in sorted(entities, key=lambda x: x['salience'], reverse=True)][:min(10, len(entities))]

    # Iterate over the entities
    for entity in entities:
        # Print the name, type, and salience of the entity
        print(f"{entity['name']}: {entity['type']} ({entity['salience']})")
    # make into a list and remove duplicates
    entities_list = list({entry['name'] for entry in top_entities})

    return entities_list


my_es = Elasticsearch(
    cloud_id = "News_DB:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRmMjc3ZjYyZDQ0Yzg0MDEyOTY2ZmRjN2M2ZTQzYjAxNiQwYTgyOGQ1ZDhlYTQ0NDc0OTExOWMzMWE5YzFmNTZiOQ==",
    http_auth = ("elastic", "U3hRNSFFEuQyeGqV2kzsdnf1")
)


latest_article_pointer = None
keyword_exists = False
while keyword_exists == False:
    # make call to elasticsearch db
    # call elasticsearch
    doc = {
        "size": 1,
        "sort": [
            {"publishedAt": "desc"},
        ],
    }
    # check if request provides pointer
    if latest_article_pointer is not None:
        doc["search_after"] = [latest_article_pointer, ]
    response = my_es.search(
        index="topic_0",
        body=doc,
    )
    latest_article_pointer = response['hits']['hits'][0]['sort'][0]
    latest_article = response['hits']['hits'][0]['_source']

    article_keywords = extract_keywords(latest_article["description"] + " " + latest_article["title"] + \
                                        " " + latest_article["content"])
    new_fields = {
        'keywords': ' '.join(article_keywords),
    }
    my_es.update(
        index="topic_0",
        id=response['hits']['hits'][0]['_id'],
        body={
            'doc': new_fields
        }
    )