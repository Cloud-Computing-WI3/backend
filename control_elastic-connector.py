import requests


def cloud_control(request):
    """
    Checks status of elastic cloud connector.
    Resumes connector if it is paused, pauses if connector ist running
    """

    # confluent cloud information
    environment_id = "env-xqnm9g"
    kafka_cluster_id = "lkc-22zo0m"
    connector_name = "ElasticsearchSinkConnector_0"
    url_string = f'https://api.confluent.cloud/connect/v1/environments/{environment_id}' \
                 f'/clusters/{kafka_cluster_id}/connectors/{connector_name}/status'
    API_Key = "PIOMXPW2EUC6EFLE"
    secret = "Dy9LQxyQo5yn23c//smhZ3LW6ehHMmtk0b9S0oHAtqoKNj36MCufPgncGnsmGEf5"

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