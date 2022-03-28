import requests
from pprint import pprint
import json
from variables import TOKEN


def list_of_public():
    response = requests.get(f'https://api.vk.com/method/'
                            f'groups.get?v=5.81&access_token='
                            f'{TOKEN}&user_id=43361902&extended=1')
    with open('publics.json', 'w') as f:
        json.dump(response.json(), f)

    for i in range(0, response.json()['response']['count']):
        pprint(response.json()['response']['items'][i]['name'])


list_of_public()