"""
This .py script provides three different endpoints / functionalitites.
It takes a request from the frontend and delivers articles based on that request.

1. Give me articles for a certain category.
2. Give me articles based on a list of keywords.
3. Give me articles based on a list of categories
"""
from elasticsearch import Elasticsearch

def fetch_articles_category(request_dict):
    page_size = 20

    # define doc for query
    doc = {
        'size': page_size,
        'query': {
            'match': {
                'category': request_dict['category_name']
            }},
        "sort": [
            {"publishedAt": "desc"},
            ],
    }
    # check if request provides pointer
    if request_dict['elastic-pointer'] is not None:
        doc['search_after'] = [request_dict['elastic-pointer']]

    # make request to elastic
    my_es = Elasticsearch(
        cloud_id="News_DB:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRmMjc3ZjYyZDQ0Yzg0MDEyOTY2ZmRjN2M2ZTQzY"
                 "jAxNiQwYTgyOGQ1ZDhlYTQ0NDc0OTExOWMzMWE5YzFmNTZiOQ==",
        http_auth=("elastic", "U3hRNSFFEuQyeGqV2kzsdnf1")
    )

    # call elasticsearch
    rezz = my_es.search(
        index='topic_0',
        body=doc,
    )

    # return articles
    return {"Articles": [article['_source'] for article in rezz['hits']['hits']],
            'elastic-pointer': rezz['hits']['hits'][page_size - 1]['sort'][0]}


request_dict = {
    "category_name": "sports",
    "elastic-pointer": 1669712565000
}

return_dict = fetch_articles_category(request_dict)

print("hallo")