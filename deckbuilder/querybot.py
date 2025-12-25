#!/usr/bin/python3

import json
import requests
import time

api = 'https://api.scryfall.com'
headers = {
    'User-Agent': 'mytestapp/0.1',
    'Accept': '*/*'
}

page_num = 1

entrypoint = 'cards/search'
options = 'format=json&include_extras=false&include_multilingual=false&include_variations=false'
query = 'delayedblastfireball'
queryfilter = 'format%3Acommander+game%3Apaper+'

# 3 pip cards, synergy with Omnath
query = '%28mana%3A%2F%5Csc%5Csc%5Csc%2F+or+%28is%3Asplit+mana%3A%2F%5Csc.%2A%5Csc.%2A%5Csc%2F%29%29'

while True:
        url = api + '/' + entrypoint + '?' + options + f'&page={page_num}' + '&q=' + queryfilter + '+' + query
        print(f'Query: {url}')
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            contents = response.json()
            # print(json.dumps(contents, indent=4))

            filename = f'response{page_num}.json'
            with open(filename, 'w') as file:
                json.dump(contents, file, indent=4)

            print(f'Wrote {len(contents.get("data", []))} to {filename}')

        else:
            print(f'Error: {response.status_code}')
            print(f"Response: {response.text}")
            break

        if contents.get('has_more', False) and 'next_page' in contents:
                url = contents.get('next_page')
                page_num += 1
                time.sleep(1.0)
        else:
                break
