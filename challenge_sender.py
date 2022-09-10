import schedule
import time
import random
import sqlite3 as sql
import json
import random
from twilio.rest import Client
import os

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

def job():
    send_challs()  
    schedule_next_run()
    return schedule.CancelJob

def send_challs():
    challenges_json = open('challenges.json')
    challenges_obj = json.load(challenges_json)
    prompt = random.randint(0, len(challenges_obj) - 1)
    
    connection = sql.connect('pairs.db')
    cursor = connection.cursor()
    statement1 = f"SELECT * FROM PAIRS WHERE Confirmed = {True}"
    cursor.execute(statement1)
    output = cursor.fetchall()
    statement2 = "UPDATE PAIRS SET ResponsesToday = '0'"
    cursor.execute(statement2)
    statement3 = f"UPDATE PAIRS SET PromptToday = {prompt}"
    cursor.execute(statement3)
    connection.commit()
    connection.close()
    challenge = f"Your LittleTexts Prompt: {challenges_obj[str(prompt)][0]['challText']}\n\n(Send in your response by replying \"RESPONSE <insert response here>\")"
    for row in output:
        name1 = row[0]
        number1 = row[1]
        name2 = row[2]
        number2 = row[3]
        sms_send(number1, challenge.replace("@@NICKNAME@@", name2))
        sms_send(number2, challenge.replace("@@NICKNAME@@", name1))

def schedule_next_run():
    time_str = '{:02d}:{:02d}'.format(random.randint(9, 17), random.randint(0, 59))
    schedule.clear()
    print("Scheduled for {}".format(time_str))
    schedule.every().day.at(time_str).do(job)

def main():
    schedule_next_run()

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
