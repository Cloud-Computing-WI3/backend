# pass -> euQ2nst@pbFmxV?
# API Key -> 6c4ca48625364ef1a6428ec31262cb18
import requests
import json
from confluent_kafka import Producer
from config import conf
import datetime
from elasticsearch import Elasticsearch


# Code for NewsAPI.org


def app(request):
    print(request)
    category_name = "technology"
    # define base url
    base_url = "https://newsapi.org/v2/top-headlines?"

    # API Key
    API_Key = "apiKey=6c4ca48625364ef1a6428ec31262cb18"

    # Build String that will be submitted for search
    submit_string = base_url + API_Key + "&" + f"category={category_name}" + "&" + "country=us" + "&" + "pageSize=100"

    # collect all
    r = requests.get(submit_string)
    print(r)
    my_dict = r.json()
    #json_string = json.dumps(my_dict, indent=4)

    # connect to Confluent to send articles to Queue
    def delivery_report(err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """
        if err:
            print('Message delivery failed: {}'.format(err))
        else:
            print(f"Message delivered {msg.value()} an topic {msg.topic()}")


    # returns JSON object as
    # a dictionary



    # Create producer
    producer = Producer(conf)

    # serialize JSON Object before sending it in

    producer.flush()
    now = datetime.datetime.now().replace(second=0, microsecond=0)


    iso_now = now.isoformat()
    # get latest article by date published, all articles older than that article will be deleted

    for article in my_dict['articles']:
        print(article)
        article['readAt'] = str(iso_now)
        article['category'] = category_name
        json_string = json.dumps(article)
        my_string = json_string.encode("utf-8")

        # send json info to kafka
        producer.produce("topic_0", my_string, callback=delivery_report, partition=0)

        # Wait for any outstanding messages to be delivered and delivery report
        # callbacks to be triggered.

        producer.flush()

        print("Alle Nachrichten an Kafka gesendet")


app("hallo")
