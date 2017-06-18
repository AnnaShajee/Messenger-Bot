import os, sys
from flask import Flask, request
from pymessenger import Bot
from wit import Wit
import requests

app= Flask(__name__)

FB_ACCESS_TOKEN = "FB_TOKEN"
FB_VERIFY_TOKEN = "hello"
WIT_ACCESS_TOKEN = "WIT_TOKEN"
WEATHER_API_KEY = "WEATHER_TOKEN"

main_intent = None
context_here = {}
sess_id = None
sender = None

bot = Bot(FB_ACCESS_TOKEN)

@app.route('/', methods=['GET'])
def verify():
    #Webhook verification
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == FB_VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Token verified", 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    print ("1\n")
    log(data)
    if data['object'] == 'page':
        print("2\n")
        for entry in data['entry']:
            print("3\n")
            for event in entry['messaging']:
                #IDs
                sender_id = event['sender']['id']
                global sender
                sender = sender_id
                recipient_id = event['recipient']['id']
                if event.get('message') and sender_id not in '1025076087628659':
                    if 'text' in event['message']:
                        global sess_id
                        sess_id = event['timestamp']
                        print("4\n session id is ", sess_id)
                        message_text = event['message']['text']
                        global context_here
                        context_here = client.run_actions(session_id = sess_id, message = message_text, context = context_here)
                        log("The session state is now:" + str(context_here))
                        print("5\n")
                    else:
                        message_text = None
                    reply= message_text + " opposum"
                    bot.send_text_message(sender, reply)
                else:
                    print("Not a message")
    else:
        return "Not a page event"
    return "ok", 200

def send(request, response):
    global sender
    bot.send_text_message(sender, "Hello")
    msg = response['text'][2:-1]
  #  bot.send_text_message(sender, response['text'])    <<<< trying to send the message to messenger
    log(response['text'])
    print("printing")
    print(msg)
    print("6 send\n")

def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val

def get_forecast(request):
    print("Started")
    context = request['context']
    entities = request['entities']
    print(entities)
    print(entities['intent'][0]['value'])
    if entities['intent'][0]['value']:
        intent = entities['intent'][0]['value']
        print("Intent exists")
        global main_intent
        if not intent == main_intent:
            main_intent = intent
            print("Global intent is", main_intent)

    loc = first_entity_value(entities, 'location')
    if loc:
        print("Location is ", loc)
        parameters = {"q": loc, "key": WEATHER_API_KEY}
        response = requests.get("http://api.apixu.com/v1/current.json", params = parameters)
        data = response.json()
        print("Here is API")
        print(data)
        if data.get('error') is not None:
            print(data['error']['message'])
            context['missingLocation'] = True
            if context.get('forecast') is not None:
                del context['forecast']
            return context
        else:
            context['forecast'] = data['current']['condition']['text']
            context['temperature'] = data['current']['temp_c']
            context['wind'] = data['current']['wind_kph']
            if context.get('missingLocation') is not None:
                del context['missingLocation']
    else:
        context['missingLocation'] = True
        if context.get('forecast') is not None:
            del context['forecast']
    print("Forecasting here")
    return context

def log(message):
    print(message)
    sys.stdout.flush()

chat_actions = {
    'send': send,
    'getForecast': get_forecast,
}

client = Wit(access_token = WIT_ACCESS_TOKEN, actions = chat_actions)

if __name__ == "__main__":
    app.run(debug = True, port = 80)
    

