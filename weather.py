#either import or use directly

import sys
import requests
from wit import Wit

WIT_ACCESS_TOKEN = "WIT_TOKEN"
WEATHER_API_KEY = "API_KEY"

def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val

def send(request, response):
    print(response['text'])

def get_forecast(request):
    context = request['context']
    entities = request['entities']

    loc = first_entity_value(entities, 'location')
    if loc:
        parameters = {"q": loc, "key": WEATHER_API_KEY}
        response = requests.get("http://api.apixu.com/v1/current.json", params = parameters)
        data = response.json()
        context['forecast'] = data['current']['condition']['text']
        context['temperature'] = data['current']['temp_c']
        context['wind'] = data['current']['wind_kph']
        if context.get('missingLocation') is not None:
            del context['missingLocation']
    else:
        context['missingLocation'] = True
        if context.get('forecast') is not None:
            del context['forecast']

    return context

actions = {
    'send': send,
    'getForecast': get_forecast,
}

client = Wit(access_token = WIT_ACCESS_TOKEN, actions=actions)
#client.interactive()
