#author mpetersbe - inspired by niyatip
from __future__ import print_function
#from apiclient import discovery
from slackclient import SlackClient
from watson_developer_cloud import ConversationV1

import os
import time

import httplib2
import json

import oauth2client
from oauth2client import client
from oauth2client import tools

import logging
logging.basicConfig()

import datetime


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"

# instantiate Slack clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

#instantiate workspace and context for Conversation service
WORKSPACE_ID = os.environ.get("WORKSPACE_ID")
USERNAME = os.environ.get("WORKSPACE_USERNAME")
PASSWORD = os.environ.get("WORKSPACE_PASSWORD")
context = {}


FLOW_MAP = {}


def set_auth_token(user, token):
    """ Exchanges an authorization flow for a Credentials object.
    Passes the token provided by authorization server redirection to this function.
    Stores user credentials.
    """
    flow = FLOW_MAP.get(user)
    if flow is not None:
        try:
            credentials = flow.step2_exchange(token)
        except oauth2client.client.FlowExchangeError:
            return -1

        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'calendar-python-quickstart-' + user + '.json')

        store = oauth2client.file.Storage(credential_path)
        print("Storing credentials at " + credential_path)
        store.put(credentials)
        return 0
    else:
        return None



    
def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands.
        If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    attachments = ""
    response = "Not sure what you mean."
    if command.startswith("token"):
        store_status = set_auth_token(user, command[6:].strip())
        if store_status is None:
            response = "You must first start the authorization process with @energy_advisor hello."
        elif store_status == -1:
            response = "The token you sent is wrong."
        elif store_status == 0:
            response = "Authentication successful!You can now communicate with Watson."
###    elif get_credentials(user) is None or command.startswith("reauth"):
###        response = "Visit the following URL in the browser: " +  get_auth_url(user) \
###                   + " \n Then send watson the authorization code like @watson token abc123."
    else :
        #Link to Watson Conversation as Auth is completed
        # Replace with your own service credentials
        conversation = ConversationV1(
            username= USERNAME,
            password= PASSWORD,
            version='2016-09-20'
        )

        #Get response from Watson Conversation
        responseFromWatson = conversation.message(
            workspace_id=WORKSPACE_ID,
            message_input={'text': command},
            context=context
        )

        #Get intent of the query
 ###       intent = responseFromWatson['intents'][0]['intent']
###
###        #Render response on Bot
###        #Format Calendar output on the basis of intent of query
###        if intent == "schedule":
###            response = "Here are your upcoming events: "
###            attachments = calendarUsage(user, intent)
###        elif intent == "free_time":
###            response = calendarUsage(user, intent)
###        else:
        response = responseFromWatson['output']['text'][0]
###
        
    slack_client.api_call("chat.postMessage", as_user=True, channel=channel, text=response,
                      attachments=attachments)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        This parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip(), \
                       output['channel'], output['user']
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel and user:
                handle_command(command, channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
