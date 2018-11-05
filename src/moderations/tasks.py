import requests
from background_task import background


@background(schedule=2)
def async_get_request(url, params):
    return requests.get(url, params)
