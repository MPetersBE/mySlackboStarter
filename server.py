#author mpetersbe - inspired by niyatip
from __future__ import print_function
from slackclient import SlackClient
from watson_developer_cloud import ConversationV1

import os
import time

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

#Link to Watson Conversation as Auth is completed
conversation = ConversationV1(
    username= USERNAME,
    password= PASSWORD,
    version='2016-09-20'
)
    
def handle_command(command, channel, user):

  attachments = ""

  #Get response from Watson Conversation
  responseFromWatson = conversation.message(
      workspace_id=WORKSPACE_ID,
      message_input={'text': command},
      context=context
  )

  #Get intent of the query
  response = responseFromWatson['output']['text'][0]
        
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

