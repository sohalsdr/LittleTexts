import requests
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import os
from twilio.rest import Client
import json
from os.path import exists as file_exists
import random
import time
import schedule

DOWNLOAD_DIRECTORY = '/home/human/Git/LittleTexts/images'
app = Flask(__name__)

def sms_send(to_number: str, body: str):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)
    send_number = os.environ['TWILIO_SEND_NUMBER']
    message = client.messages \
                    .create(
                        body=body,
                        from_=send_number,
                        to=to_number
                    )
    
    print(message.sid)

def send_prompt():
    config_json = open('config.json')
    config_obj = json.load(config_json)
    
    challenges_json = open('challenges.json')
    challenges_obj = json.load(challenges_json)
    
    random1 = random.randint(0, len(challenges_obj) - 1)
    random2 = random.randint(0, len(challenges_obj) - 1)
    sms_send(config_obj['user1'][0]['phoneNumber'], f"Your LittleTexts Prompt: {challenges_obj[str(random1)][0]['challText'].replace('@@NICKNAME@@', config_obj['user2'][0]['nickname'])}")
    sms_send(config_obj['user2'][0]['phoneNumber'], f"Your LittleTexts Prompt: {challenges_obj[str(random2)][0]['challText'].replace('@@NICKNAME@@', config_obj['user1'][0]['nickname'])}")
    
    data_json = open('data.json')
    data_obj = json.load(data_json)
    data_obj['user1'][0]['expectingResponse'] = True
    data_obj['user2'][0]['expectingResponse'] = True
    data_obj['user1'][0]['currentChallenge'] = random1
    data_obj['user2'][0]['currentChallenge'] = random2
    data_obj['user1'][0]['pastChallenges'].append(random1)
    data_obj['user2'][0]['pastChallenges'].append(random2)

    with open('data.json','w') as jsonFile:
        json.dump(data_obj, jsonFile)
        


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    from_number = request.values.get('From')
    body = request.values.get('Body', None)
    
    config_json = open('config.json')
    config_obj = json.load(config_json)

    challenges_json = open('challenges.json')
    challenges_obj = json.load(challenges_json)

    data_json = open('data.json')
    data_obj = json.load(data_json)

    if from_number == config_obj['user1'][0]['phoneNumber'] and data_obj['user1'][0]['expectingResponse']:
        resp = MessagingResponse()
        resp.message("Thanks for responding!")
        
        sms_send(config_obj['user2'][0]['phoneNumber'], f"From LittleTexts: {challenges_obj[str(data_obj['user1'][0]['currentChallenge'])][0]['responseTemplate'].replace('@@NICKNAME@@', config_obj['user1'][0]['nickname'])}")
        
        sms_send(config_obj['user2'][0]['phoneNumber'], body)
        
        data_obj['user1'][0]['expectingResponse'] = False
        with open('data.json','w') as jsonFile:
            json.dump(data_obj, jsonFile)
                
        return str(resp)
    
    if from_number == config_obj['user2'][0]['phoneNumber'] and data_obj['user2'][0]['expectingResponse']:
        resp = MessagingResponse()
        resp.message("Thanks for responding!")
        
        sms_send(config_obj['user1'][0]['phoneNumber'], f"From LittleTexts: {challenges_obj[str(data_obj['user2'][0]['currentChallenge'])][0]['responseTemplate'].replace('@@NICKNAME@@', config_obj['user2'][0]['nickname'])}")
        
        sms_send(config_obj['user1'][0]['phoneNumber'], body)
        
        data_obj['user2'][0]['expectingResponse'] = False
        with open('data.json','w') as jsonFile:
            json.dump(data_obj, jsonFile)
        
        return str(resp)

if __name__ == "__main__":
    if not file_exists("data.json"):
        data_obj = {}
        data_obj['user1'] = []
        data_obj['user1'].append({
            'expectingResponse': False,
            'currentChallenge': None,
            'pastChallenges': []
        })
        data_obj['user2'] = []
        data_obj['user2'].append({
            'expectingResponse': False,
            'currentChallenge': None,
            'pastChallenges': []
        })
        
        with open('data.json','w') as jsonFile:
            json.dump(data_obj, jsonFile)
         
    schedule_send()
    app.run(debug=False)
