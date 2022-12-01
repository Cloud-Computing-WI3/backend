from datetime import datetime, time, timedelta
from pydantic import BaseModel
from typing import Union, List

class Category(BaseModel):
    name: str

class Article(BaseModel):
    publishedAt: Union[datetime, None] = None
    author: Union[str, None] = None
    urlToImage: Union[str, None] = None
    description: Union[str, None] = None
    source: Union[object, None] = None
    readAt: Union[datetime, None] = None
    url: Union[str, None] = None
    category: Union[str, None] = None

class ArticleRequest(BaseModel):
    elastic_pointer: Union[str, None] = None
    category_name: Union[str, None] = None

class ArticleResponse(BaseModel):
    elastic_pointer: Union[str, None] = None
    articles: List[Article]