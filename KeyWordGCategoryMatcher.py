"""
This code grabs all the articles from the DB that have the same readAt (so one batch) and categorises them / adds keywords
until the articles in the next Batch have been labeled.


Pseudo Algo:
Call the elastic endpoint
Get the newest timestamp (a)
Get the next timestamp after (b)
Grab all the articles for the timestamp (a) and label them with keywords / categories
Write them back into elasticsearch
call next batch / check if they have been labeled
"""

import requests
from elasticsearch import Elasticsearch
from datetime import datetime

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


# create elasticsearch client
my_elastic = Elasticsearch(
    cloud_id="News_DB:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRmMjc3ZjYyZ"
             "DQ0Yzg0MDEyOTY2ZmRjN2M2ZTQzYjAxNiQwYTgyOGQ1ZDhlYTQ0NDc0OTExOWMzMWE5YzFmNTZiOQ==",
    http_auth=("elastic", "U3hRNSFFEuQyeGqV2kzsdnf1")
)

latest_article_pointer = None
# Iterate over Articles until the sun turns cold
while True:
    # call elasticsearch, get the newest readAt article
    doc = {
        "size": 1,
        "sort": [
            {"readAt": "desc"},
        ],
    }
    # check if request provides pointer
    if latest_article_pointer is not None:
        doc["search_after"] = [latest_article_pointer, ]
    response = my_elastic.search(
        index="topic_0",
        body=doc,
    )
    latest_article_pointer = response['hits']['hits'][0]['sort'][0]
    latest_article = response['hits']['hits'][0]['_source']
    # check if keyword exists
    """
    # if latest_article['keywords'] is not None:
    #    print('article has keywords')
    #    exit()
    """
    # now let's grab all the entries with that particular timestamp
    # convert string to actual timestamp
    query = {
        "query": {
            "match_phrase": {
                "readAt": latest_article['readAt']
            }
        }
    }
    # Execute elasticsearch scrolling, to get all articles within that batch
    # Initialize the scroll
    page = my_elastic.search(
        index="topic_0",
        body=query,
        scroll='2m',
        size=1,
    )
    sid = page['_scroll_id']
    original_scroll_size = page['hits']['total']['value']
    print(f'total scroll size of current batch {original_scroll_size}')
    # Start scrolling
    print("Scrolling...")
    while (original_scroll_size > 0):
        # Add Google Keywords and Categories
        for hit in page['hits']['hits']:
            print(f'current scroll: {original_scroll_size} with: author: {hit["_source"]["author"]}, '
                  f'readAt: {hit["_source"]["readAt"]}'
                  f' title: {hit["_source"]["title"]}')
            # extract article keywords
            article_keywords = extract_keywords(
                (hit["_source"]["description"] or "") + " " + (hit["_source"]["title"] or "") +
                " " + (hit["_source"]["content"] or ""))

            # identify category according to google
            article_google_category = identify_google_category((hit["_source"]["description"] or "") + " "
                                                               + (hit["_source"]["title"] or "") +
                                                               " " + (hit["_source"]["content"] or ""))
            # add keywords as new field to entry
            new_fields = {
                'keywords': ' '.join(article_keywords),
                'google_categories': ' '.join(article_google_category)
            }
            # write modified entry into elasticsearch db
            my_elastic.update(
                index="topic_0",
                id=hit['_id'],
                body={
                    'doc': new_fields
                }
            )

        page = my_elastic.scroll(scroll_id=sid, scroll='2m')
        # Update the scroll ID
        sid = page['_scroll_id']
        original_scroll_size -= 1







   # response = my_elastic.search(index="topic_0", body=query)

    print('elo')




