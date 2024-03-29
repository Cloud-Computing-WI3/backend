"""
This code grabs all the articles from the DB that have the same readAt (so one batch) and categorises them / adds keywords.
Continues until it finds articles that already have been labeled before.


Pseudo Algo:
Call the elastic endpoint
Get the newest timestamp (a)
Get the next timestamp after (b)
Grab all the articles for the timestamp (a) and label them with keywords / categories
Write them back into elasticsearch
call next batch (based on timestamp b) / check if they have been labeled
"""

import requests
from elasticsearch import Elasticsearch
from config import keyword_google_matcher_config
from datetime import datetime


def extract_keywords(text):
    """
    This method extracts all the keywords using the google natural language API based on a given Text.
    :param text: Text from which the keywords are to be extracted.
    """
    # Set the API key for the Google Natural Language Processing API
    api_key = keyword_google_matcher_config['google_api_key']
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
    """
    This method identifies a category using the google natural language API based on a given Text.
    :param text: Text from which the category is to be identified.
    """
    # Set the API key for the Google Natural Language Processing API
    api_key = keyword_google_matcher_config['google_api_key']
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

def keyword_category_labeler(request):
    # create elasticsearch client instance
    my_elastic = Elasticsearch(
        cloud_id=keyword_google_matcher_config['elastic_cloud_id'],
        http_auth=(keyword_google_matcher_config['elastic_cloud_user'], keyword_google_matcher_config['elastic_cloud_pass'])
    )

    latest_article_pointer = None
    # Iterate over Articles until the sun turns cold, batches have been labeled or there are no more articles to label.
    while True:
        # call elasticsearch, get the newest readAt article
        doc = {
            "size": 20,
            "sort": [
                {"readAt": "desc"},
            ],
        }
        # check if request provides pointer, if so then set it in the doc
        if latest_article_pointer is not None:
            doc["search_after"] = [latest_article_pointer, ]
        # perform query
        response = my_elastic.search(
            index="topic_0",
            body=doc,
        )
        # Extract article and pointer
        latest_article_pointer = response['hits']['hits'][0]['sort'][0]
        latest_article = response['hits']['hits'][0]['_source']
        # check if keyword exists, if so then exit
        if 'keywords' in latest_article.keys():
            print('article has keywords')
            exit()

        # now let's grab all the entries with that particular timestamp
        query = {
            "query": {
                "match_phrase": {
                    "readAt": latest_article['readAt']
                }
            }
        }
        # Execute elasticsearch scrolling, to get all articles within that batch and initialize the scroll
        page = my_elastic.search(
            index="topic_0",
            body=query,
            scroll='2m',
            size=1,
        )
        # extract id for scrolling
        sid = page['_scroll_id']
        # save original scroll size
        scroll_size = page['hits']['total']['value']
        print(f'total scroll size of current batch {scroll_size}')
        # Start scrolling
        print("Scrolling...")
        # scroll until there are no more results
        while (scroll_size > 0):
            # Add Google Keywords and Categories
            for hit in page['hits']['hits']:
                print(f'current scroll: {scroll_size} with: author: {hit["_source"]["author"]}, '
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
                        "doc": {
                            "keywords": ' '.join(article_keywords),
                            "google_categories": ' '.join(article_google_category)
                        }}
                )
            # let's scrollll
            page = my_elastic.scroll(scroll_id=sid, scroll='2m')
            # Update the scroll ID
            sid = page['_scroll_id']
            # reduce scroll size, indicating article has been labeled
            scroll_size -= 1

keyword_category_labeler('hallo')