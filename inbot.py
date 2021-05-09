import os
import time
import re
from slackclient import SlackClient
import pandas as pd

# instantiate Slack client
slack_token = os.environ['SLACK_BOT_TOKEN']
slack_client = SlackClient(slack_token)
in_channel = os.environ['IN_CHANNEL']
announcements = os.environ['ANNOUNCEMENTS']
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Slack Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        
        # [IN]box
        print("Sending inbox")
        response = slack_client.api_call("users.list")
        members = response['members']
        users = {}
        for person in members:
            if not person['deleted'] and not person['is_bot']:
                users[person['profile']['real_name']] = person['id']
        
        df = pd.read_csv('inbox.csv')
        recipients = df['To'].unique()
        
        for recipient in recipients:
            dm = slack_client.api_call(
                "conversations.open",
                users=users[recipient]
            )
            messages = df.loc[df['To']==recipient]
            for _, row in messages.iterrows():
                name = row['From']
                if row['Anonymous'] == 'Yes':
                    name = "Anonymous"
                slack_client.api_call(
                    "chat.postMessage",
                    channel=dm['channel']['id'],
                    text="From " + name + ": " + row['Message']
                )

        # Record po[IN]ts for senders
        print("Recording points")
        response = slack_client.api_call(
                "chat.postMessage",
                channel=in_channel,
                text="Po[IN]ts for [IN]box:"
            )
        senders = df['From'].unique()
        for sender in senders:
            sent = df.loc[df['From']==sender]
            points = min(len(sent.index), 5)
            response = slack_client.api_call(
                "chat.postMessage",
                channel=in_channel,
                text=sender + ": " + str(points)
            )
        
        # Send new [IN]box prompt
        prompts = [
            "Write a message to someone you’d like to get to know better.",
            "Share your favorite song with someone!",
            "Write a midterm season motivational message to someone.",
            "Write a message to someone you haven’t written an [IN]box to yet.",
            "Write to someone you’ve shared your favorite memory with in PBL!",
            "Send your best joke to someone who you think could use a smile :)",
            "Share your spring break adventures with someone!",
            "Recommend someone your current / all-time favorite book / movie / tv-show !!",
            "Share your best pick-up line with someone ;)",
            "Write a thank you note to someone!"
        ]
        n = 1 # TODO: change number
        response = slack_client.api_call(
                "chat.postMessage",
                channel=announcements,
                text="[IN]box #" + str(n) + ": " + prompts[n - 1]
            )

    else:
        print("Connection failed. Exception traceback printed above.")