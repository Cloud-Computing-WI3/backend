#   News Feed Service
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
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?&style=for-the-badge&logo=redis&logoColor=white)

### Prerequisites
* [Redis.io](https://redis.io/)


### Redis (in-memory caching)

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

# Deployment 
![Cloud functions](https://codelabs.developers.google.com/static/codelabs/cloud-starting-cloudfunctions-v2/img/51b03178ac54a85f.png)
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
# Deployment 
<img src="https://storage.googleapis.com/gweb-cloudblog-publish/images/cloud-scheduler-512-color.max-600x600.png" width="200" height="200" alt="Cloud scheduler">
This section describes the configuration of the [Google cloud scheduler](https://cloud.google.com/scheduler?hl=en) that is used to interact with the cloud functions. 
### Configuration steps 
At first the name, frequency and timezone have to be defined. The timezone should be the same one as the google cloud functions run on. The Frequency is defined using the [cron job format](https://cloud.google.com/scheduler/docs/configuring/cron-job-schedules#defining_the_job_schedule). 
![Cloud Scheduler one](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/cloud_scheduler1.png)
After having configured this part a new mask comes up. The address of the cloud function, auth type have to be configured accordingly in order ot execute the cloud function deployed before. 
![Cloud Scheduler two](https://github.com/Cloud-Computing-WI3/.github/blob/main/images/cloud_scheduler2.png)
Some optional settings can be configured additionally, however this is unecessary for our this case. 
# Deployment 
![Confluent Kafka](https://cdn.confluent.io/wp-content/uploads/seo-logo-meadow.png)
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
