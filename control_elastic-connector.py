import requests
from config import cloud_control_conf

def cloud_control(request):
    """
    Checks status of elastic cloud connector.
    Resumes connector if it is paused, pauses if connector ist running.
    :param request: Does not really matter, only there so it works.
    """

    # confluent cloud information
    environment_id = cloud_control_conf['environment_id']
    kafka_cluster_id = cloud_control_conf['kafka_cluster_id']
    connector_name = cloud_control_conf['connector_name']
    API_Key = cloud_control_conf['API_Key']
    secret = cloud_control_conf['secret']

    url_string = f'https://api.confluent.cloud/connect/v1/environments/{environment_id}' \
                 f'/clusters/{kafka_cluster_id}/connectors/{connector_name}/status'


    # check connector status
    r = requests.get(url=url_string, auth=(API_Key, secret)).json()
    status = r['connector']['state']

    if status == "PAUSED":
        # activate elastic-connector-sink
        print("elastic cloud connector is paused, trying to resume it")
        url_string = f'https://api.confluent.cloud/connect/v1/environments/{environment_id}' \
                     f'/clusters/{kafka_cluster_id}/connectors/{connector_name}/resume'
        r = requests.put(url=url_string, auth=(API_Key, secret))
        print(r)

    elif status == "RUNNING":
        # stop elastic-connector-sink
        print("elastic cloud connector is running, trying to pause it ")
        url_string = f'https://api.confluent.cloud/connect/v1/environments/{environment_id}' \
                     f'/clusters/{kafka_cluster_id}/connectors/{connector_name}/pause'
        r = requests.put(url=url_string, auth=(API_Key, secret)).json()
        print(r)

cloud_control('hallo')