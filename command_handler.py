from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import sqlite3 as sql
from os.path import exists as file_exists
import os
import json
import threading
from subprocess import call
from challenge_sender import send_challs

app = Flask(__name__)

def thread_second():
    call(["python", "challenge_sender.py"])

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

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    from_number = request.values.get('From')

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    if body == "RESETDB" and from_number == os.environ['ADMIN_NUMBER']:
        drop_table  = "DROP TABLE IF EXISTS PAIRS"
        new_table = """ CREATE TABLE PAIRS (
            Name1 VARCHAR(25) NOT NULL,
            Number1 VARCHAR(12) NOT NULL,
            Name2 VARCHAR(25) NOT NULL,
            Number2 VARCHAR(12) NOT NULL,
            Streak INT NOT NULL,
            PromptToday INT,
            ResponsesToday INT,
            Confirmed BOOLEAN NOT NULL
        ); """
        connection = sql.connect('pairs.db')
        cursor = connection.cursor()
        cursor.execute(drop_table)
        cursor.execute(new_table)
        connection.commit()
        connection.close()
        resp.message("Database Erased")
    elif body == "SENDMSG" and from_number == os.environ['ADMIN_NUMBER']:
        send_challs()
        resp.message("Challenge Sent")
    elif body == 'START':
        resp.message("Welcome to LittleTexts! To get started, text me the command \"REGISTER <your nickname> <partner\'s nickname> <partner\'s phone number (including country code)>\"\n(ex. REGISTER Jesse Walter +14445556666)\n\nFor more information, read the documentation located at DOCS_SITE")
    elif body.startswith("REGISTER"):
        args = body.split(" ")
        nick = args[1]
        number = from_number
        partner_nick = args[2]
        partner_number = args[3]
        connection = sql.connect('pairs.db')
        cursor = connection.cursor()
        statement1 = f"SELECT * FROM PAIRS WHERE Number1 = '{number}'"
        cursor.execute(statement1)
        number1check = cursor.fetchall()
        statement2 = f"SELECT * FROM PAIRS WHERE Number2 = '{number}'"
        cursor.execute(statement2)
        number2check = cursor.fetchall()
        statement3 = f"SELECT * FROM PAIRS WHERE Number1 = '{partner_number}'"
        cursor.execute(statement3)
        partnernumber1check = cursor.fetchall()
        statement4 = f"SELECT * FROM PAIRS WHERE Number2 = '{partner_number}'"
        cursor.execute(statement4)
        partnernumber2check = cursor.fetchall()
        if len(number1check) != 0 or len(number2check) != 0:
            resp.message(f"It appears you're already registered in the system!")
        elif len(partnernumber1check) != 0 or len(partnernumber2check) != 0:
            resp.message(f"It appears your partner is already registered in the system!")
        else:
            cursor.execute("INSERT INTO PAIRS (Name1, Number1, Name2, Number2, Streak, PromptToday, ResponsesToday, Confirmed) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (nick, number, partner_nick, partner_number, 0, None, 0, False))
            statement = f"SELECT * FROM PAIRS WHERE Number1 = '{number}'"
            cursor.execute(statement)
            output = cursor.fetchall()
            for row in output:
                print(row)
            connection.commit()
            connection.close()
            resp.message(f"Created pair with the following data:\n\nYour Name: {nick}\nYour Phone Number: {number}\nPartner's Name: {partner_nick}\nPartner's Number: {partner_number}\n\nYour partner will recieve an SMS asking them to confirm this.")
            confirmation_message = f"This is LittleTexts, a service to help couples connect through random daily challenges! You're recieving this message because \"{nick}\" ({number}) has requested to pair with you. To confirm, please reply \"CONFIRM {number}\"."
            sms_send(partner_number, confirmation_message)
    elif body.startswith("CONFIRM"):
        args = body.split(" ")
        connection = sql.connect('pairs.db')
        cursor = connection.cursor()
        statement = f"SELECT Number1 FROM PAIRS WHERE Number2 = '{from_number}'"
        cursor.execute(statement)
        output = cursor.fetchone()
        connection.commit()
        connection.close()
        submitted_number = output[0]
        if args[1] == submitted_number:
            connection = sql.connect('pairs.db')
            cursor = connection.cursor()
            statement = f"UPDATE PAIRS SET Confirmed = '1' WHERE Number2 = '{from_number}'"
            cursor.execute(statement)
            connection.commit()
            connection.close()
            sms_send(submitted_number, "Your partner has confirmed! You and your partner will now recieve daily LittleTexts challenges.")
            resp.message("Thanks for confirming! You and your partner will now recieve daily LittleTexts challenges.")
        else:
            resp.message("Uh-oh, looks like the phone number didn't match what we have in the system. Please check for any typos and try again!")
    elif body.startswith("RESPONSE "):
        number = from_number
        connection = sql.connect('pairs.db')
        cursor = connection.cursor()
        statement1 = f"SELECT * FROM PAIRS WHERE Number1 = '{number}'"
        cursor.execute(statement1)
        number1check = cursor.fetchone()
        statement2 = f"SELECT * FROM PAIRS WHERE Number2 = '{number}'"
        cursor.execute(statement2)
        number2check = cursor.fetchone()
        if not number1check and not number2check:
            connection.commit()
            connection.close()
            resp.message("Uh oh, your number doesn't seem to be in the system! Please try replying \"START\" to get set up!")
        else:
            challenges_json = open('challenges.json')
            challenges_obj = json.load(challenges_json) 
            
            text = body[9:]
            
            if number1check:
                number = number1check[3]
                nick = number1check[2]
                prompt = number1check[5]
                responses_today = number1check[6]
                streak = number1check[4]
            else:
                number = number2check[1]
                nick = number2check[0]
                prompt = number2check[5]
                responses_today = number2check[6]
                streak = number2check[4]
            sms_send(number, challenges_obj[str(prompt)][0]['responseTemplate'].replace("@@NICKNAME@@", nick))
            sms_send(number, text)
            statement3 = f"UPDATE PAIRS SET ResponsesToday = '{responses_today}'"
            cursor.execute(statement3)
            if responses_today > 1:
                statement4 = f"UPDATE PAIRS SET Streak = '{streak + 1}'"
                cursor.execute(statement4)
            connection.commit()
            connection.close()
    elif body == 'STATUS':
        number = from_number
        connection = sql.connect('pairs.db')
        cursor = connection.cursor()
        statement1 = f"SELECT * FROM PAIRS WHERE Number1 = '{number}'"
        cursor.execute(statement1)
        number1check = cursor.fetchall()
        statement2 = f"SELECT * FROM PAIRS WHERE Number2 = '{number}'"
        cursor.execute(statement2)
        number2check = cursor.fetchall()
        if len(number1check) == 0 and len(number2check) == 0:
            connection.commit()
            connection.close()
            resp.message("Uh oh, your number doesn't seem to be in the system! Please try replying \"START\" to get set up!")
        else:
            statement3 = f"SELECT * FROM PAIRS WHERE Number1 = '{number}' OR Number2 = {number}"
            cursor.execute(statement3)
            output = cursor.fetchone()
            name1 = output[0]
            number1 = output[1]
            name2 = output[2]
            number2 = output[3]
            streak = output[4]
            confirmed = output[7]
            resp.message(f"Info:\n\n{name1}: {number1}\n{name2}: {number2}\nConfirmed: {confirmed}\nStreak: {streak}")
    else:
        resp.message("You've reached LittleTexts, a service to help couples connect through random daily challenges! To learn more, please visit our website at DOCS_SITE")
    return str(resp)

if __name__ == "__main__":
    if not file_exists('pairs.db'):
        connection = sql.connect('pairs.db')
        cursor = connection.cursor()
        table = """ CREATE TABLE PAIRS (
            Name1 VARCHAR(25) NOT NULL,
            Number1 VARCHAR(12) NOT NULL,
            Name2 VARCHAR(25) NOT NULL,
            Number2 VARCHAR(12) NOT NULL,
            Streak INT NOT NULL,
            PromptToday INT,
            ResponsesToday INT,
            Confirmed BOOLEAN NOT NULL
        ); """
        cursor.execute(table)
        connection.commit()
        connection.close()
    processThread = threading.Thread(target=thread_second)
    processThread.start()
    app.run(debug=True)