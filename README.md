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
