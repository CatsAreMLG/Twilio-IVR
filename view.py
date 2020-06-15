from flask import (
    Flask,
    redirect,
    request,
    url_for,
)
from twilio.twiml.voice_response import VoiceResponse
from twilio.twiml.messaging_response import Message, MessagingResponse
from twilio.rest import Client
from view_helpers import twiml

from settings import ACCOUNT_SID, AUTH_TOKEN, SMS_DESTINATION

app = Flask(__name__)


@app.route('/ivr/welcome', methods=['POST'])
def welcome():
    response = VoiceResponse()
    with response.gather(
        num_digits=1,
        timeout=5,
        action=url_for('menu'),
        method="POST"
    ) as g:
        g.say(message="Thanks for calling The Helper Bees support line. " +
              "Please press 1 for concerns about a client. " +
              "Press 2 for notifying us about missing your shift. " +
              "Press 3 for questions about client payments. " +
              "Press 4 for questions about your timesheet. " +
              "Press 5 for inquiries on new client availability. " +
              "For all other questions or concerns press 6. " +
              "If you need me to repeat the options press 0. "
              )

    response.say('We didn\'t receive any input. Goodbye.')
    return twiml(response)


@app.route('/ivr/menu', methods=['POST'])
def menu():
    selected_options = request.form["Digits"]

    option_actions = {
        '1': 'client_concerns',
        '2': 'missed_shifts',
        '3': 'client_payments',
        '4': 'timesheet_questions',
        '5': 'client_availability',
        '6': 'other',
        '0': 'welcome'
    }

    if selected_options in option_actions:
        response = VoiceResponse()
        response.redirect(url_for(option_actions[selected_options]))
        return twiml(response)

    return _redirect_welcome()


@app.route('/ivr/transcribe', methods=['POST'])
def transcribe():
    if 'SpeechResult' in request.form:
        transcription = request.form['SpeechResult']
        source = request.form['To']
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        client.messages.create(
            body=transcription,
            from_=source,
            to=SMS_DESTINATION
        )

        return _redirect_hangup()
    else:
        return _no_input()


@app.route('/ivr/client_payments', methods=['POST'])
def client_payments():
    response = _gather_voice("Please leave us your first and last name. " +
                             "The client\'s first and last name. " +
                             "and a brief description about the question or issue you have."
                             )

    return twiml(response)


@app.route('/ivr/timesheet_questions', methods=['POST'])
def timesheet_questions():
    response = _gather_voice("Please leave us your first and last name. " +
                             "and what questions or inquiries you have about your timesheet."
                             )

    return twiml(response)


@app.route('/ivr/client_availability', methods=['POST'])
def client_availability():
    response = _gather_voice("Please leave us your first and last name. " +
                             "How many clients you are looking to pick up. " +
                             "And what times you are available for new clients."
                             )

    return twiml(response)


@app.route('/ivr/other', methods=['POST'])
def other():
    response = _gather_voice("Please leave us your first and last name. " +
                             "And a brief description about what issue or question you have."
                             )

    return twiml(response)


@app.route('/ivr/client_concerns', methods=['POST'])
def client_concerns():
    return _call_redirect()


@app.route('/ivr/missed_shifts', methods=['POST'])
def missed_shifts():
    return _call_redirect()


# private methods

def _gather_voice(voice):
    response = VoiceResponse()
    with response.gather(
        input="speech",
        speechModel="phone_call",
        speechTimeout='auto',
        action=url_for('transcribe'),
        actionOnEmptyResult=True,
        method="POST"
    ) as g:
        g.say(voice)

    return response


def _no_input():
    response = VoiceResponse()

    response.say("We didn\'t receive any input. " +
                 "Returning to the main menu. ")
    response.redirect(url_for('welcome'))

    return twiml(response)


def _call_redirect():
    response = VoiceResponse()

    response.say("Redirecting to our agent. Please hold.")
    response.dial(SMS_DESTINATION)

    return twiml(response)


def _redirect_welcome():
    response = VoiceResponse()

    response.say("Returning to the main menu")
    response.redirect(url_for('welcome'))

    return twiml(response)


def _redirect_hangup():
    response = VoiceResponse()

    response.say(
        "Thank you. We\'ll forward your message and have someone call you back. Goodbye.")
    response.hangup()

    return twiml(response)


if __name__ == "__main__":
    app.run(debug=True)
