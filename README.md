<img src="https://github.com/sohalsdr/LittleTexts/raw/main/LT_Bubble_Logo.png" alt="drawing" width="200"/>

# LittleTexts

###### A service to help couples connect through random daily challenges!

LittleTexts is an SMS-based chatbot powered by Twilio, Python, Flask, and SQLite that messages you and your partner open-ended writing "challenges". Every day, at a random time, all LittleTexts users will recieve they day's prompt. They will then have until the next prompt to reply to the bot with their answer to the challenge. The bot will then forward that answer to their partner, creating a fun talking point and facilitating sharing more little moments!

---

## Installation/Usage

This version of LittleTexts is a work in progress and not currently suitable for real-world(sage). 

### How to install

1. Clone the Git repository to your local/development machine and make sure Python is installed

2. Install all python packages necessary through `pip install -r requirements.txt`

3. Create a file called `twilio.env` and add your TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_SEND_NUMBER, and ADMIN_NUMBER

4. Run `python3 command_handler.py`

### How to use

To use the bot, start by enrolling by texting the word "`START`". The bot will then prompt you to run `REGISTER <your_name> <partner's_name> <partner's_phone_number>` (ex. `REGISTER Jesse Walter +14445556666`) to add yourself to the service, and the bot will send a confirmation message to your partner to make sure they consent to being texted by LittleTexts
