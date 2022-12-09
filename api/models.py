from datetime import datetime, time, timedelta
from pydantic import BaseModel
from typing import Union, List, Dict

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

class CategoriesAndPointers(BaseModel):
    name: Dict[Union[str, None], Union[str, None]]
