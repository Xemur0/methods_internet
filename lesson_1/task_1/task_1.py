import json
import requests

victim = 'Xemur0'

response = requests.get(f'https://api.github.com/users/{victim}/repos')

with open('repos.json', 'w') as f:
    json.dump(response.json(), f)

for i in response.json():
    print(i['name'])

