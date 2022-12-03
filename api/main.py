from elasticsearch import Elasticsearch
from fastapi import FastAPI, Response
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from api.models import Article, ArticleResponse, Category

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
@app.get("/articles", response_model=ArticleResponse)
def read_articles(category_name: str, elastic_pointer: str = None):
    page_size = 20

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

    # make request to elastic
    my_es = Elasticsearch(
        cloud_id="News_DB:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRmMjc3ZjYyZDQ0Yzg0MDEyOTY2ZmRjN2M2ZTQzY"
                 "jAxNiQwYTgyOGQ1ZDhlYTQ0NDc0OTExOWMzMWE5YzFmNTZiOQ==",
        http_auth=("elastic", "U3hRNSFFEuQyeGqV2kzsdnf1")
    )

    # call elasticsearch
    request = my_es.search(
        index="topic_0",
        body=doc,
    )
    articles = []
    for article in request["hits"]["hits"]:
        raw_article = article["_source"]
        c = Category(**raw_article["source"])
        if c.name.lower() == "youtube":
            a = Article(
                publishedAt=raw_article["publishedAt"],
                author=raw_article["author"],
                urlToImage="https://stileex.xyz/wp-content/uploads/2019/06/download-youtube-video-1.png",
                description=raw_article["title"],
                readAt=raw_article["readAt"],
                url=raw_article["url"],
                title=raw_article["title"],
                category=c,
            )
        else:

            a = Article(
                publishedAt=raw_article["publishedAt"],
                author=raw_article["author"],
                urlToImage=raw_article["urlToImage"],
                description=raw_article["description"],
                readAt=raw_article["readAt"],
                url=raw_article["url"],
                category=c,
            )
        articles.append(a)
    # return articles
    elastic_pointer = request["hits"]["hits"][page_size - 1]["sort"][0]
    return ArticleResponse(elastic_pointer=elastic_pointer, articles=articles)


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