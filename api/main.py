from elasticsearch import Elasticsearch
from fastapi import FastAPI, Response, Request
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from api.models import Article, ArticleResponse, Source, ArticlesCategoriesResponse, CategoriesAndPointers
from iteround import saferound
from fastapi.encoders import jsonable_encoder

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
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def call_elastic_search(doc: dict) -> dict:
    # make request to elastic
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


def get_articles_and_pointer(res, page_size: int = 20) -> tuple[list, str]:
    articles = []
    for article in res["hits"]["hits"]:
        raw_article = article["_source"]

        s = Source(**raw_article["source"])
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
    elastic_pointer = res["hits"]["hits"][page_size - 1]["sort"][0]
    return articles, elastic_pointer


@app.get("/articles", response_model=ArticleResponse)
def read_articles(category_name: str, page_size: int = 20, elastic_pointer: str = None):
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
    articles, pointer = get_articles_and_pointer(res=response, page_size=page_size)
    return ArticleResponse(elastic_pointer=pointer, articles=articles)


@app.get("/articles_by_keywords", response_model=ArticleResponse)
def read_articles_by_keyword(keywords: str, elastic_pointer: str = None):
    page_size = 20
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
    # check if request provides pointer
    if elastic_pointer is not None:
        doc["search_after"] = [elastic_pointer, ]
    response = call_elastic_search(doc=doc)
    articles, pointer = get_articles_and_pointer(res=response, page_size=page_size)
    return ArticleResponse(elastic_pointer=pointer, articles=articles)



"""
Expecting Request body with following schema: 
{
    categories_and_pointers : { "category_name1" : "pointer1", 
                                "category_name2" : "pointer2",
                                "category_name3" : "pointer3"}
}
"""


@app.post("/articles_by_categories", response_model=ArticlesCategoriesResponse)
async def read_articles_by_categories(categories_and_pointers_body: CategoriesAndPointers):
    # unpack to json
    categories_and_pointers = jsonable_encoder(categories_and_pointers_body)["name"]
    page_size = 20
    # calculate individual page_size based on number of categories
    round_list = saferound([page_size / len(categories_and_pointers) for x in categories_and_pointers], places=0)
    page_sizes = {key: None for (key, value) in categories_and_pointers.items()}
    # get keys as list
    key_list = list(page_sizes.keys())
    # match categories to values, convert to int
    for i in range(0, len(round_list)):
        page_sizes[key_list[i]] = int(round_list[i])

    articles = []
    elastic_pointers = {}

    for category_name, pg_size in page_sizes.items():
        elastic_pointer_response, articles_response = read_articles(category_name, pg_size,
                                                                    categories_and_pointers[category_name])
        elastic_pointers[category_name] = elastic_pointer_response[1]
        articles.extend([article for article in articles_response[1]])

    return ArticlesCategoriesResponse(articles=articles, pointers=elastic_pointers)

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
