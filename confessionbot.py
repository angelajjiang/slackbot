import os
import time
import re
from slackclient import SlackClient
import pandas as pd

# instantiate Slack client
slack_token = os.environ['SLACK_BOT_TOKEN']
slack_client = SlackClient(slack_token)
confessions_channel = os.environ['CONFESSIONS_CHANNEL']
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Slack Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]

        # Confessions
        df = pd.read_csv('confessions.csv')
        i = 1 # TODO: change number
        for _, row in df.iterrows():
            slack_client.api_call(
                    "chat.postMessage",
                    channel=confessions_channel,
                    text=str(i) + ". " + row['Confession']
                )
            i += 1

    else:
        print("Connection failed. Exception traceback printed above.")