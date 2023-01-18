# pass -> euQ2nst@pbFmxV?
# API Key -> 6c4ca48625364ef1a6428ec31262cb18
import requests
import json
from confluent_kafka import Producer
from config import conf
import datetime
from elasticsearch import Elasticsearch


# Code for NewsAPI.org

# boolean if the database is empty, set to true
first_run = True
def publish_news(request):
    """
    Publishes News from Newsapi.org to confluent kafka on the cloud. Checks with elasticsearch and only publishes
    articles that are newer than the latest article from the elastic db.
    :param request: Makes sure that it works on google cloud function.
    :return:
    """

    def process_category(category_name):
        """
        Takes a category, calls Newsapi.org and sends articles to kafka.
        :param category_name: Name of the category for which articles are to be retrieved.
        """
        # Build String that will be submitted for search
        submit_string = base_url + api_key + "&" + f"category={category_name}" + "&" + \
                        "country=us" + "&" + "pageSize=100"
        # variable to check if an HTTPError was raised in order to skip the rest of the function
        httperror = False
        try:
            r = requests.get(submit_string)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"HTTPError occured while calling the NewsAPI {err}, exiting script")
            # set httperror to true
            httperror = True

        if not httperror:
            print(r)
            my_dict = r.json()
            # connect to Confluent to send articles to Queue
            def delivery_report(err, msg):
                """ Called once for each message produced to indicate delivery result.
                    Triggered by poll() or flush(). """
                if err:
                    print('Message delivery failed: {}'.format(err))
                else:
                    print(f"Message delivered {msg.value()} an topic {msg.topic()}")

            # Create producer
            producer = Producer(conf)

            # flushing just to be sure
            producer.flush()
            # get current time down to the second
            now = datetime.datetime.now().replace(second=0, microsecond=0)
            # transform date format to iso 8601
            iso_now = now.isoformat()
            # create Elasticsearch instance
            my_es = Elasticsearch(
                cloud_id="News_DB:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRmMjc3ZjYyZDQ0Yzg0MDEyOTY2ZmRjN2M2ZTQzYjAxNiQwYTgyOGQ1ZDhlYTQ0NDc0OTExOWMzMWE5YzFmNTZiOQ==",
                http_auth=("elastic", "U3hRNSFFEuQyeGqV2kzsdnf1")
            )
            # if it's not the first run then skip this part, there are no entries in the db!
            if not first_run:
                # look for latest entry inside category
                rezz = my_es.search(
                    index='topic_0',
                    size=1,
                    query={"query_string": {"query": category_name, "fields": ["category"]}},
                    sort={"publishedAt": {"order": "desc", "unmapped_type": "date"}}
                )
                # grab the latest time from the first (0th entry) record
                latest_article_time = rezz['hits']['hits'][0]['_source']['publishedAt']
                # dict with articles that are newer than latest article from elastic db
                new_articles = []
                # check all articles to see which are newer than latest article from db
                for article in my_dict['articles']:
                    # is the article newer than my latest article timestamp?
                    if article['publishedAt'] > latest_article_time:
                        # if so append it to my list
                        new_articles.append(article)
            elif first_run:
                new_articles = []
                # check all articles to see which are newer than latest article from db
                for article in my_dict['articles']:
                    new_articles.append(article)

            # does my list actually have entries?
            if len(new_articles) != 0:
                print(len(new_articles), " published to kafka")
                # it does -> iterate over articles and write them into the datastructure
                for article in new_articles:
                    print(article)
                    # add time that article is processed
                    article['readAt'] = str(iso_now)
                    # add article category
                    article['category'] = category_name
                    json_string = json.dumps(article)
                    my_string = json_string.encode("utf-8")
                    # send json info to kafka
                    producer.produce("topic_0", my_string, callback=delivery_report, partition=0)
                    # Wait for any outstanding messages to be delivered and delivery report
                    # callbacks to be triggered.
                    producer.flush()

                print("Alle Messages sent to kafka")
            elif len(new_articles) == 0:
                print("Nothing to send, no new Articles found :(")

    print(request)
    # define base url, top-headlines
    base_url = "https://newsapi.org/v2/top-headlines?"
    # API Key for newsapi.org
    api_key = "apiKey=6c4ca48625364ef1a6428ec31262cb18"
    # categories
    my_categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
    for category in my_categories:
        process_category(category)


publish_news("hallo")
