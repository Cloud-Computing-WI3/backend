from elasticsearch import Elasticsearch
# create Elasticsearch index

my_es = Elasticsearch(
    cloud_id = "News_DB:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRmMjc3ZjYyZDQ0Yzg0MDEyOTY2ZmRjN2M2ZTQzYjAxNiQwYTgyOGQ1ZDhlYTQ0NDc0OTExOWMzMWE5YzFmNTZiOQ==",
    http_auth = ("elastic", "U3hRNSFFEuQyeGqV2kzsdnf1")
)



#rezz = my_es.search(index="topic_0", q="publishedAt")
rezz = my_es.search(
    index='topic_0',
    size=1,
    sort= {"publishedAt": {"order": "desc", "unmapped_type": "date"}}
    )
# grab the latest time from the first (0th entry) record
latest_article_time = rezz['hits']['hits'][0]['_source']['publishedAt']

# grab records from that day / hour, get latest date published


print("hello")