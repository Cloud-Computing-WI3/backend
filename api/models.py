from datetime import datetime, time, timedelta
from pydantic import BaseModel
from typing import Union, List, Dict
"""
This file defines all the models used by FastAPI in the main.py
"""


class Source(BaseModel):
    id: Union[str, None] = None
    name: str = ""

class PointerDict(BaseModel):
    categoryname: str
    point: str

class Article(BaseModel):
    publishedAt: Union[datetime, None] = None
    author: Union[str, None] = None
    urlToImage: Union[str, None] = None
    description: Union[str, None] = None
    readAt: Union[datetime, None] = None
    url: Union[str, None] = None
    source: Source = None
    title: Union[str, None] = None
    category_name: Union[str, None] = None

class ArticleRequest(BaseModel):
    elastic_pointer: Union[str, None] = None
    category_name: Union[str, None] = None

class ArticleResponse(BaseModel):
    elastic_pointer: Union[str, None] = None
    articles: List[Article]

class ArticlesCategoriesResponse(BaseModel):
    articles: List[Article]
    pointers: Dict[str, str]


class CategoryPointer(BaseModel):
    name: str
    pointer: Union[str, None]


class CategoriesAndPointers(BaseModel):
    categories: List[CategoryPointer]

class GoogleCategory(BaseModel):
    category: str
    name: str