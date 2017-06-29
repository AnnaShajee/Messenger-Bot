
import os, sys
import requests
from wit import Wit
from flask import Flask, request
import json
from random import shuffle
import pprint
#from pymessenger import Bot

app= Flask(__name__)

FB_ACCESS_TOKEN = "EAADZCHPUR2IUBAAkXRzFxlrja0bsoRaNffcfGGcy3fOTnwMIS9ZAu8B7jDKRpTZCfRxHLZCCmBA74466ZCyUPHZCjjalb3CiRU6hSfTF1Nwb2B0j9YYZCWD1FWabflDdQOF100WZClBVHHXDq4Xiii7CNLz0OpvlTvSffvkivhftDgZDZD"
FB_VERIFY_TOKEN = "hello"
WIT_ACCESS_TOKEN = "NEQRIBEGFNFLKWGR5NK7LOJ7SX4S336M"
WEATHER_API_KEY = "bbc4cc6f61484782824133116170506"
CLIENT_ID = "Y3HMWY5DG1OJRCC3ULU3P2O25KW4WTQM5ZUGSZW3PMH5AKST"
CLIENT_SECRET = "BU5SRP2QYZZS2EPHXH5YOGWVLX3OVIJGWU4AX3RUQPCWG1SR"

context_here = {}
past = None
main_intent = None
sess_id = None
sender = None

#bot = Bot(FB_ACCESS_TOKEN)

# Facebook Messenger GET Webhook
@app.route('/', methods=['GET'])
def verify():
    #Webhook verification
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == FB_VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Token verified", 200

# Facebook Messenger POST Webhook
@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    log(data)
    if data['object'] == 'page':
        for entry in data['entry']:
            # get all the messages
            for event in entry['messaging']:
                #IDs
                sender_id = event['sender']['id']
                recipient_id = event['recipient']['id']
                if event.get('message') and sender_id not in '1025076087628659':
                    if 'text' in event['message']:
                        global sess_id
                        global context_here
                        sess_id = event['timestamp']
                        global past
                        if sess_id == past:
                            return "Old news", 200
                        else:
                            past = sess_id
                            context_here = {}
                        message_text = event['message']['text']
                        context_here = client.run_actions(session_id = sender_id, message = message_text, context = context_here)
                        
                        log("The session state is now:" + str(context_here))
                    else:
                        message_text = None
                    #bot.send_text_message(sender, reply)
                else:
                    print("Not a message")
    else:
        return "Not a page event"
    return "ok", 200


def fb_message(sender_id, text):
    """
    Function for returning response to messenger
    """
    data = {
        'recipient': {'id': sender_id},
        'message': {'text': text}
    }
    # Setup the query string with your PAGE TOKEN
    qs = 'access_token=' + FB_PAGE_TOKEN
    # Send POST request to messenger
    resp = requests.post('https://graph.facebook.com/me/messages?' + qs,
                         json=data)
    return resp.content


def first_entity_value(entities, entity):
    #Return first entity value
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val


def send(request, response):
    #Sender function
    
    fb_id = request['session_id']
    text = response['text']
    # send message
    post_facebook_message(fb_id,text.decode('utf-8'))


def get_forecast(request):
    log("##333333 In forecast 444444444")
    context = request['context']
    entities = request['entities']
    log(context)
    log(entities)
    if context.get('missingEvent') is not None:
        del context['missingEvent']
    if context.get('result') is not None:
        del context['result']
    if context.get('missingLocation') is not None:
        del context['missingLocation']
    if context.get('errorWeather') is not None:
        del context['errorWeather']
    if context.get('errorEvent') is not None:
        del context['errorEvent']
    if entities['intent'][0]['value']:
        intent = entities['intent'][0]['value']
        print("Intent exists")
        if not intent == main_intent:
            main_intent = intent
            print("Global intent is", main_intent)
    else:
        if main_intent != 'weather':
            context = get_event(request)
            log(context)
            return context
    loc = first_entity_value(entities, 'location')
    if loc:
        # This is where we  use a weather service api to get the weather.
        parameters = {"q": loc, "key": WEATHER_API_KEY}
        response = requests.get("http://api.apixu.com/v1/current.json", params = parameters)
        data = response.json()
        print(data)
        if data.get('error') is not None:
            print(data['error']['message'])
            context['errorWeather'] = True
            if context.get('forecast') is not None:
                del context['forecast']
                del context['wind']
                del context['temperature']
            return context
        else:
            if context.get('forecast') is not None:
                del context['forecast']
                del context['wind']
                del context['temperature'] 
            context['forecast'] = data['current']['condition']['text']
            context['temperature'] = data['current']['temp_c']
            context['wind'] = data['current']['wind_kph']
    else:
        context['missingLocation'] = True
        if context.get('forecast') is not None:
            del context['forecast']
            del context['wind']
            del context['temperature']
    return context

def get_event(request):
    log("1111111 In Events 222222") 
    context = request['context']
    entities = request['entities']
    log(context)
    log(entities)
    if context.get('result') is not None:
        del context['result']
    if context.get('missingLocation') is not None:
        del context['missingLocation']
    if context.get('errorWeather') is not None:
        del context['errorWeather']
    if context.get('errorEvent') is not None:
        del context['errorEvent']
    if context.get('forecast') is not None:
            del context['forecast']
            del context['wind']
            del context['temperature']
    global main_intent
    if entities['intent'][0]['value']:
        intent = entities['intent'][0]['value']
        print("Intent exists")
        if not intent == main_intent:
            main_intent = intent
            print("Global intent is", main_intent)
    else:
        if main_intent != 'event':
            context = get_forecast(request)
            log(context)
            return context
    loc = first_entity_value(entities, 'location')
    if loc:
        eve = first_entity_value(entities, 'local_search_query')
        if eve:
            parameters = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "m": "foursquare", "v":20161016, "near": loc, "limit":10, "query": eve, "radius": 10000}
            response = requests.get("https://api.foursquare.com/v2/venues/explore", params = parameters)
            data = response.json()
            #pprint.pprint(data)
            if 'errorDetail' in data['meta']:
                context['errorEvent'] = data['meta']['errorDetail']
                log(data('meta')('errorDetail'))
                log(context)
                return context
            for entry in data['response']:
                if data['response']['totalResults'] == 0:
                    context['errorEvent'] = "No results found"
                    log("No results found in ",loc)
                    log(context)
                    return context
                else:
                    #if 
                    num = min(10, data['response']['totalResults'], key = lambda x: int(x))
                    trial = []
                    entry = data['response']['groups'][0]['items']
                    for index in range(num):
                        strnew = ', '.join(data['response']['groups'][0]['items'][index]['venue']['location']['formattedAddress'])
                        str = data['response']['groups'][0]['items'][index]['venue']['name']+", a " + data['response']['groups'][0]['items'][index]['venue']['categories'][0]['name'] + " at " + strnew
                        trial.append(str)
                    log(trial)
                    shuffle(trial)
                    context['result'] = trial[0]
                    say = ["Why don't you try", "You could visit", "Drop by", "Try out", "I recommend", "How about"]
                    shuffle(say)
                    context['say'] = say[0]
        else:
            context['missingEvent'] = True
    else:
        context['missingLocation'] = True

    return context
        
def log(message):
    print(message)
    sys.stdout.flush()

# Setup Actions
chat_actions = {
    'send': send,
    'getForecast': get_forecast,
    'getEvent': get_event,
}

client = Wit(access_token = WIT_ACCESS_TOKEN, actions = chat_actions)

def post_facebook_message(fbid, received_message):           

	post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAADZCHPUR2IUBAAkXRzFxlrja0bsoRaNffcfGGcy3fOTnwMIS9ZAu8B7jDKRpTZCfRxHLZCCmBA74466ZCyUPHZCjjalb3CiRU6hSfTF1Nwb2B0j9YYZCWD1FWabflDdQOF100WZClBVHHXDq4Xiii7CNLz0OpvlTvSffvkivhftDgZDZD'
	response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":received_message}})
	status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)

if __name__ == "__main__":
    app.run(debug = True, port = 80)
