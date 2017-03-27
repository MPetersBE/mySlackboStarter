########
from slackclient import SlackClient
from watson_developer_cloud import ConversationV1

import os
import time

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"

# instantiate Slack clients
sc = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

#instantiate workspace and context for Conversation service
WORKSPACE_ID = os.environ.get("WORKSPACE_ID")
USERNAME = os.environ.get("WORKSPACE_USERNAME")
PASSWORD = os.environ.get("WORKSPACE_PASSWORD")

CHANNEL_NAME = "energybot"

#Link to Watson Conversation as Auth is completed
# Replace with your own service credentials
conversation = ConversationV1(
username= USERNAME,
password= PASSWORD,
version='2017.03.27')

def main():
    # Connect to slack
    if sc.rtm_connect():
        # Send first message
        sc.rtm_send_message(CHANNEL_NAME, "Hello! I am here to help yopu!")

        while True:
            # Read latest messages
            for slack_message in sc.rtm_read():
                message = slack_message.get("text")
                user = slack_message.get("user")
                if not message or not user:
                    continue
                #Get response from Watson Conversation
                responseFromWatson = conversation.message(
                    workspace_id=WORKSPACE_ID,
                    message_input={'text': command},
                    context=context
                response = responseFromWatson['output']['text'][0] 
                sc.api_call("chat.postMessage", as_user=True, channel=channel, text=response,
                      attachments=attachments)
                sc.rtm_send_message(CHANNEL_NAME, "<@{}> wrote something...".format(user))
            # Sleep for half a second
            time.sleep(0.5)
    else:
        print("Couldn't connect to slack")

if __name__ == '__main__':
    main()
