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
    top_entities = [entity for entity in sorted(entities, key=lambda x: x['salience'], reverse=True)][
                   :min(10, len(entities))]

    # Iterate over the entities
    for entity in entities:
        # Print the name, type, and salience of the entity
        # print(f"{entity['name']}: {entity['type']} ({entity['salience']})")
        pass
    # make into a list and remove duplicates
    entities_list = list({entry['name'] for entry in top_entities})

    return entities_list


def identify_google_category(text):
    # Set the API key for the Google Natural Language Processing API
    api_key = 'AIzaSyCRHHSb8Mqw22QlcILOoWwypjHs2FqBrR0'
    # Set the text to analyze

    # Set the API endpoint URL
    api_url = "https://language.googleapis.com/v1/documents:classifyText?key=" + api_key

    # Set the document to be sent to the API
    document = {
        "type": "PLAIN_TEXT",
        "content": text
    }

    # Set the request headers
    headers = {
        "Content-Type": "application/json"
    }

    # Set the request body
    body = {
        "document": document
    }

    # Send a POST request to the API
    category_response = requests.post(api_url, json=body, headers=headers)

    # Check the response status code
    if category_response.status_code == 200:
        # Parse the response JSON
        response_json = category_response.json()
        category_names = []
        # Loop through the categories in the response
        for category in response_json["categories"]:
            # Print the name and confidence level of the category
            # print(f"Category: {category['name']}, Confidence: {category['confidence']}")
            # save only the category name on the last "/" seperator argument
            category_names.append(category['name'].split("/")[-1])
        return category_names

    else:
        # Print the error message
        print(f"Error: {category_response.text}")
        return ''


my_es = Elasticsearch(
    cloud_id="News_DB:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRmMjc3ZjYyZDQ0Yzg0MDEyOTY2ZmRjN2M2ZTQzYjAxNiQwYTgyOGQ1ZDhlYTQ0NDc0OTExOWMzMWE5YzFmNTZiOQ==",
    http_auth=("elastic", "U3hRNSFFEuQyeGqV2kzsdnf1")
)

latest_article_pointer = None

while True:
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
    # check if keyword exists
    if latest_article['keywords'] is not None:
        print('article has keywords')
        exit()

    for entry in response['hits']['hits']:
        print(entry['_id'], entry['_source']['publishedAt'], entry['_source']['readAt'])

    # extract article keywords
    article_keywords = extract_keywords((latest_article["description"] or "") + " " + (latest_article["title"] or "") +
                                        " " + (latest_article["content"] or ""))

    # identify category according to google
    article_google_category = identify_google_category((latest_article["description"] or "") + " "
                                                       + (latest_article["title"] or "") +
                                                       " " + (latest_article["content"] or ""))
    # add keywords as new field to entry
    new_fields = {
        'keywords': ' '.join(article_keywords),
        'google_categories': ' '.join(article_google_category)
    }
    # write modified entry into elasticsearch db
    my_es.update(
        index="topic_0",
        id=response['hits']['hits'][0]['_id'],
        body={
            'doc': new_fields
        }
    )
