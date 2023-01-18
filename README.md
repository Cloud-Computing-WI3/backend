![Logo](https://avatars.githubusercontent.com/u/117459812?s=200&v=4)
#   Newsify - News Feed Service
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?&style=for-the-badge&logo=redis&logoColor=white)
![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?&style=for-the-badge&logo=googlecloud&logoColor=white)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-%23005571.svg?&style=for-the-badge&logo=elasticsearch&logoColor=white)
![ElasticCloud](https://img.shields.io/badge/ElasticCloud-%23005571.svg?&style=for-the-badge&logo=elasticcloud&logoColor=white)
![Confluence](https://img.shields.io/badge/ConfluentKafka-%23172B4D.svg?&style=for-the-badge&logo=&logoColor=white)



## Table of Content
- [Getting started](#getting-started)
- [Deployment](#deployment)
    - Redis (in-memory caching)
    - Google Cloud Functions
    - Google Cloud Scheduler
    - Confluent Kafka
    - Elasticsearch
    - Elastic Cloud
- [Repository Overview](#repository-overview)


##  Getting started
1. Open a  terminal window inside this folder (`backend`)
2. Run `python3 -m venv venv` to install virtual environment
3. Activate virtual environment
    - Windows User run `.\venv\Scripts\activate`
    - Mac Users run `source ./venv/bin/activate`
4. Install requirements
`pip install -r requirements.txt`

    Notice: API-Files are stored in the sub-folder `api`
4. Start API by running `uvicorn api.main:app --reload`
5. API will be accessible via [ http://127.0.0.1:8000](http://127.0.0.1:8000)
6. Open [http://127.0.0.1:8000/docs]( http://127.0.0.1:8000/docs) to see Swagger-API documentation 


##  Deployment

### Redis (in-memory caching) 
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?&style=for-the-badge&logo=redis&logoColor=white)

[Redis](https://redis.io/) is an open-source data store that provides powerful in-memory 
caching functionality. "Newsify" implements redis using the so-called 
[cache-aside pattern](https://redis.com/solutions/use-cases/caching/) to improve 
overall latency while at the same time reducing load on ElasticSearch.

#### Deployment steps
1. Download/Installation of *RedisInsight* as GUI-Tool (optional)
   1. Download available [here](https://redis.com/redis-enterprise/redis-insight/)

2. Set up the Redis instance [here](https://redis.com). Then follow the [Redis client quickstart guide](https://docs.redis.com/latest/rc/rc-quickstart/).

3. After completing the steps in the instructions, the necessary information for the connection is available in the Redis Cloud Console. Select the created instance (see figure) and copy the relevant data:

   * **database Name:** newsify-redis-cache-0
   * **public Endpoint:** redis-19498.c238.us-central1-2.gce.cloud.redislabs.com:19498
   * **password:** *******************

4. Set up connection to redis client in python backend. After you imported `redis` you can [create a redis client](https://medium.com/codesphere-cloud/getting-started-with-redis-7964e968eae6). Also see `api/main.py` for reference.

> **Good to know**: The `set`-function can be used in Redis to store data. The parameter `ex` 
> defines the duration how long the entry is kept in the database. In the case of *Newsify*, a 
> time-to-live (TTL) of 10 minutes (600 seconds) is set. However, it might be useful in the 
> future to adjust the value of the parameter to achieve a good balance between actuality of 
> the data and efficiency of the cache (goal: maximize cache hits).

The *RedisInsights* GUI can be used to track which key-value pairs are currently stored.
To access data in Redis via python, the `get`-function can then be called in combination with the searched key.
For further implementation details refer to `api/main.py` or the [official redis-py docs](https://redis.readthedocs.io/en/latest/). 

## Google Cloud Functions 
<img src="https://codelabs.developers.google.com/static/codelabs/cloud-starting-cloudfunctions-v2/img/51b03178ac54a85f.png" width="50" height="50" alt="Cloud function">

This section descripes the deployment of code to the google cloud function service. 
### [Google Cloud Functions](https://cloud.google.com/functions)
Google Cloud Functions allows a user to run small snippets of code as a function in the cloud. It provides an endpoint that can be called to pass arguments and activate the function. 
### Deployment steps 
The first mask asks the user to enter a name for the function which defines the endpoint of the function itself. This endpoint will be used by the cloud scheduler to activate a function. 
![Mask Cloud Function one](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/cloud_function_1.png)

Aside from the name, a maximum runtime, max number of instances and so on can also be defined. However this is not necessary to deploy the code but the size of the instance could be reduced in order to save cost. 
![Mask Cloud function two](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/cloud_function2.png)
After configuring the cloud function the code itself can be added. 
![Mask Cloud function three](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/cloud_function3.png)
In the next mask, the correct coding language (and version) and entry point has to be chosen. The entry point is the name of the (first) function that is to be executed when the endpoint is called. 


## Google Cloud Scheduler 
<img src="https://storage.googleapis.com/gweb-cloudblog-publish/images/cloud-scheduler-512-color.max-600x600.png" width="50" height="50" alt="Cloud scheduler">

This section describes the configuration of the [Google cloud scheduler](https://cloud.google.com/scheduler?hl=en) that is used to interact with the cloud functions. 
### Configuration steps 
At first the name, frequency and timezone have to be defined. The timezone should be the same one as the google cloud functions run on. The Frequency is defined using the [cron job format](https://cloud.google.com/scheduler/docs/configuring/cron-job-schedules#defining_the_job_schedule). 
![Cloud Scheduler one](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/cloud_scheduler1.png)
After having configured this part a new mask comes up. The address of the cloud function, auth type have to be configured accordingly in order ot execute the cloud function deployed before. 
![Cloud Scheduler two](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/cloud_scheduler2.png)
Some optional settings can be configured additionally, however this is unecessary for our this case. 


## Confluent Kafka 
<img src="https://cdn.confluent.io/wp-content/uploads/seo-logo-meadow.png" width="200" height="200" alt="Confluent Kafka">

This section describes the deployment, setup and configuration of the Confluent Cloud environment. 
### Configuration steps 
At first a new kafka environment has to be chosen, the free one should be sufficient.
![Kafka1](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/kafka_env1.png)
Now a cloud provider has to be selected, in our case Google Cloud is the correct provider. 
![Kafka2](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/kafka_env2.png)
After the kafka environment is setup a cluster has to be configured
![Kafka3](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/kafka_env3.png)
As before, the FREE plan should be sufficient. Just click through the configuration.
![Kafka4](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/kafka_env4.png)
Now a topic has to be created that in which the messages can be written. 
In order to extract these messages to elasticsearch a new connector has to be created 
-> In the Connectors tab select an elasticsearch Service sink connector. 
Select the topic from which the messages are to be extracted. 
![Connector1](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/connector1.png)
You can define an access option, Global access is the easiest, hence it will be selected for this use case.
![Connector2](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/connector2.png)
In the next step kafka wants the connection details from an elasticsearch cloud instance. 
![Connector3](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/connector_user.png)
To find the connection URI go to 'Manage Cluster' 
Then click 'Copy endpoint', don't forget to add the correct port '9243 and enter user credentials. 
![el-conn-conf1](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/elastic_config1.png)
![el-conn-conf2](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/elastic_config1.png)
In the configuration settings, select JSON and make sure that the configuration matches the screenshot. This step is very important, all the settings must match. Otherwise the connector will not work!
![adv_config](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/advanced%20configuration.png)
Select the smallest instance, review the settings and launch the connector. 
Confluent can now send messages to elasticsearch! 

## Elastic Cloud
<img src="https://mms.businesswire.com/media/20191022005864/en/751270/22/elastic-logo-H-full_color.jpg" width="50" height="50" alt="Elastic Cloud">

This section describes the configuration & deployment of an [Elastic Cloud](https://cloud.google.com/scheduler?hl=en) instance that is used to store articles.
### Configuration steps 
Setting up the Elastic cloud instance is very easy but a few things are imnportant: 1. Make sure to select the smallest size possible, otherwise the instance will cost 600+ Dollars a month. 2. Select the right version 3. Write down the elastic user that can be used to access the database. 
![elastic_deploy1](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/elastic1.png)
![elastic_deploy2](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/elastic2.png)
![elastic_deploy3](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/elastic3.png)

# Configuration 
After having configured & deployed the different cloud services, the API Keys, URLs and so on will have to be added to the 'config.py' file. 

##  Repository Overview
```
Backend
├── api
│   ├── google_categories.py
│   ├── main.py
│   ├── models.py
│   └── test.py
├── app.yaml
├── config.py
├── control_elastic-connector.py
├── Dockerfile
├── KeyWordGCategoryMatcher.py
├── Publish_News.py
├── README.md
├── requirements.txt
├── schema.json
└── WebScraper.py
```
