import requests
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import os
from twilio.rest import Client
import json
from os.path import exists as file_exists
import firebase_admin
from firebase_admin import firestore

DOWNLOAD_DIRECTORY = '/home/human/Git/LittleTexts/images'
app = Flask(__name__)

def sms_send(client: Client, to_number: str, body: str):
    send_number = os.environ['TWILIO_SEND_NUMBER']
    message = client.messages \
                    .create(
                        body=body,
                        from_=send_number,
                        to=to_number
                    )
    
    print(message.sid)


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    body = request.values.get('Body', None)
    
    if body == "START":
        resp = MessagingResponse()
        resp.message("Welcome to LittleTexts! To set up your Pair, text me the words \"CREATE PAIR\"")

    """
    if request.values['NumMedia'] != '0':

        # Use the message SID as a filename.
        filename = request.values['MessageSid'] + '.png'
        with open('{}/{}'.format(DOWNLOAD_DIRECTORY, filename), 'wb') as f:
           image_url = request.values['MediaUrl0']
           f.write(requests.get(image_url).content)

        resp.message("Thanks for the image!")
    else:
        # Get the message the user sent our Twilio number
        body = request.values.get('Body', None)

        # Start our TwiML response
        resp = MessagingResponse()

        print(body)
        resp.message("eeeee")
    """

    return str(resp)

if __name__ == "__main__":
    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)
    
    app = firebase_admin.initialize_app()
    db = firestore.client()

    sms_send(client, os.environ['ADMIN_NUMBER'], "Server starting!")
    app.run(debug=False)
