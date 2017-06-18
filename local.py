import sys
from wit import Wit
import requests

WIT_ACCESS_TOKEN = "NEQRIBEGFNFLKWGR5NK7LOJ7SX4S336M"
WEATHER_API_KEY = "bbc4cc6f61484782824133116170506"

client = Wit(access_token = WIT_ACCESS_TOKEN, actions=actions)

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
"""
def wit_response(message_text):
    response = client.message(message_text)
    #entity = None
    #value = None
    intent = None

    try:
        intent = response['intent']
        for 
        #entity = list(resp['entities'])[0]
        #value = resp['entities'][entity][0]['value']
        
    except:
        pass
    #return (entity, value)
    return(intent)
"""
