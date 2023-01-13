from elasticsearch import Elasticsearch
from fastapi import FastAPI, Response, Request
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from api.models import Article, ArticleResponse, Source, ArticlesCategoriesResponse, CategoriesAndPointers, \
    GoogleCategory
from iteround import saferound
from fastapi.encoders import jsonable_encoder
from typing import Union, List
from api.google_categories import GOOGLE_CATEGORIES
import sys
import json
import redis
"""
This file is the Backend API Component, it utilizes FastAPI, communicates with elasticsearch / redis and the frontend. 
It's responsible for sending articles back and forth. 
Three main endpoints are implemented: 
- read_articles()
- read_articles_by_keyword()
- read_articles_by_categories()

"""




# constants
REDIS_TTL = 600  # keep alive for redis cache in seconds

# Create FastAPI instance
app = FastAPI(
    title="News Feed Service",
    version="0.0.1",
    terms_of_service="#",
    contact={
        "name": "Cloud Computing Topic #2",
        "url": "#",
        "email": "#",
    },
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"}
)

# Define endpoints for CORS Middleware
origins = [
    "http://localhost:3000",
    "https://cohesive-slate-368310.uc.r.appspot.com"
]

# Define middleware component for FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def redis_connect() -> redis.client.Redis:
    """
    This function connects to a redis client.
    """
    try:
        # create instance
        client = redis.Redis(
            host="redis-19498.c238.us-central1-2.gce.cloud.redislabs.com",
            port=19498,
            password="mxXW82wuWLgieV2nm3rpykH3tqytY52Y",
            db=0,
            socket_timeout=5,
        )
        # ping client
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        print("AuthenticationError")
        sys.exit(1)


redis_client = redis_connect()


def call_elastic_search(doc: dict) -> dict:
    """
    This function is responsible for calling the elasticsearch cloud instance.
    """
    # Create Elasticsearch instance
    my_es = Elasticsearch(
        cloud_id="News_DB:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRmMjc3ZjYyZDQ0Yzg0MDEyOTY2ZmRjN2M2ZTQzY"
                 "jAxNiQwYTgyOGQ1ZDhlYTQ0NDc0OTExOWMzMWE5YzFmNTZiOQ==",
        http_auth=("elastic", "U3hRNSFFEuQyeGqV2kzsdnf1")
    )
    # call elasticsearch
    response = my_es.search(
        index="topic_0",
        body=doc,
    )
    return response


def get_articles_and_pointer(res) -> tuple[list, str]:
    """
    Map elasticsearch response into the FastAPI Article Model so it can be send to the Frontend.
    :param res: This parameter is the elasticsearch result that contains articles.
    """
    articles = []
    # make sure we don't have duplicate articles
    unique_articles = set()
    # iterate over articles in res
    for article in res["hits"]["hits"]:
        # get article itself
        raw_article = article["_source"]
        if raw_article["publishedAt"] in unique_articles:
            continue
        # add to set, duplicates will be removed because of datastructure (set)
        unique_articles.add(raw_article["publishedAt"])
        # check the name of the source
        s = Source(**raw_article["source"])
        # if it's a youtube video we want to give it a generic image link
        if s.name.lower() == "youtube":
            a = Article(
                publishedAt=raw_article["publishedAt"],
                author=raw_article["author"],
                urlToImage="https://stileex.xyz/wp-content/uploads/2019/06/download-youtube-video-1.png",
                description=raw_article["title"],
                readAt=raw_article["readAt"],
                url=raw_article["url"],
                title=raw_article["title"],
                Source=s,
                category_name=raw_article["category"]
            )
        else:
            # all other articles...
            a = Article(
                publishedAt=raw_article["publishedAt"],
                author=raw_article["author"],
                urlToImage=raw_article["urlToImage"],
                description=raw_article["description"],
                readAt=raw_article["readAt"],
                url=raw_article["url"],
                title=raw_article["title"],
                category_name=raw_article["category"],
                source=raw_article["source"]
            )
        articles.append(a)
    # get elastic pointer of last article
    elastic_pointer = res["hits"]["hits"][-1]["sort"][0]
    return articles, elastic_pointer


@app.get("/articles", response_model=ArticleResponse)
def read_articles(category_name: str, page_size: int = 20, elastic_pointer: str = None, bypass_cache: bool = False):
    """
    First of three main endpoints.
    Read articles for every predefined category, uses cache-aside pattern in order to minimize requests to elastic
    and loading times.
    :param category_name: Names of categories.
    :param page_size: Number of articles to be send to frontend.
    :param elastic_pointer: Elastic pointer for 'search_after' parameter.
    :param bypass_cache: Defines wether to ignore redis cache.
    """
    # create key for redis in-memory caching
    redis_key = category_name if elastic_pointer is None else category_name + elastic_pointer

    # check if data in redis cache
    data = redis_client.get(redis_key)

    # if cache hit --> serve from cache
    if data is not None and not bypass_cache:
        print("serve from cache...")
        json_data = json.loads(data)
        return ArticleResponse(elastic_pointer=json_data["pointer"], articles=json_data["articles"])

    # if cache miss --> go to api and write to cache
    elif data is None or bypass_cache:
        # define doc for query
        doc = {
            "size": page_size,
            "query": {
                "match": {
                    "category": category_name
                }},
            "sort": [
                {"publishedAt": "desc"},
            ],
        }
        # check if request provides pointer
        if elastic_pointer is not None:
            doc["search_after"] = [elastic_pointer, ]
        response = call_elastic_search(doc=doc)
        articles, pointer = get_articles_and_pointer(res=response)
        print("serve from api...")

        if bypass_cache:
            return ArticleResponse(elastic_pointer=pointer, articles=articles)

        # save response to redis and serve afterwards
        elif articles and not bypass_cache:
            state = redis_client.set(redis_key, json.dumps(
                {
                    "articles": jsonable_encoder(articles),
                    "pointer": pointer
                }
            ), ex=REDIS_TTL)

            if state is True:
                return ArticleResponse(elastic_pointer=pointer, articles=articles)


@app.get("/articles_by_keywords", response_model=ArticleResponse)
def read_articles_by_keyword(keywords: str, page_size: int = 20, elastic_pointer: str = None):
    """
        Second of three main endpoints.
        This endpoint gives results for keywords and supports an elastic_pointer in order to do utilize the 'search_after'
        parameter of elasticsearch.
        :param keywords: Keywords for which to look in the elasticsearch DB.
        :param page_size: Number of articles to be delivered.
        :param elastic_pointer: Elastic Pointer to be utilized by the 'search_after' parameter in elasticsearch.

        """
    keyword_list = keywords.split(",")
    # define doc for query
    doc = {
        "size": page_size,
        "query": {
            "bool": {
                # should is roughly equivalent to boolean OR
                "should": [{"match": {"description": keyword}} for keyword in keyword_list]
            }
        },
        "sort": [
            {"publishedAt": "desc"},
        ],
    }
    # check if request provides pointer, if so set pointer
    if elastic_pointer is not None:
        doc["search_after"] = [elastic_pointer, ]
    response = call_elastic_search(doc=doc)
    articles, pointer = get_articles_and_pointer(res=response)
    return ArticleResponse(elastic_pointer=pointer, articles=articles)


@app.post("/articles_by_categories", response_model=ArticlesCategoriesResponse)
async def read_articles_by_categories(categories_and_pointers_body: CategoriesAndPointers, page_size: int = 20):
    """
    Third of the three main endpoints.
    :param categories_and_pointers_body: Body that contains a list of multiple objects = [{'category_name' : name,
    'pointer': pointer_value}].
    :param page_size: Number of results.
    """
    # unpack to json
    categories_and_pointers = jsonable_encoder(categories_and_pointers_body)["categories"]
    # calculate individual page_size based on number of categories
    round_list = saferound([page_size / len(categories_and_pointers) for x in categories_and_pointers], places=0)
    page_sizes = dict()
    for category in categories_and_pointers:
        page_sizes[category["name"]] = None
    # get keys as list
    key_list = list(page_sizes.keys())
    # match categories to values, convert to int
    for i in range(0, len(round_list)):
        page_sizes[key_list[i]] = int(round_list[i])

    articles = []
    elastic_pointers = {}
    # make a call to elastic via 'read_articles' for each chosen category.
    for category_name, pg_size in page_sizes.items():
        elastic_pointer_response, articles_response = read_articles(category_name, pg_size, next(
            item["pointer"] for item in categories_and_pointers if item["name"] == category_name))
        elastic_pointers[category_name] = elastic_pointer_response[1]
        articles.extend([article for article in articles_response[1]])

    return ArticlesCategoriesResponse(articles=articles, pointers=elastic_pointers)


@app.get("/google_categories", response_model=Union[GoogleCategory, List[GoogleCategory]])
async def read_google_articles():
    categories = [GoogleCategory(**cat) for cat in GOOGLE_CATEGORIES]
    return categories


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="News Feed Service",
        version="0.0.1",
        description="This is a very custom OpenAPI schema",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
