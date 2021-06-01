from getRandomUser import get_random_reviewer, create_reviewer
import os
# Use the package we installed
from slack_bolt import App
from slack_sdk import WebClient

# Slack bolt - wtf
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

def get_user_info(user_id):
    result = client.users_info(user=user_id)
    return result["user"]["profile"]["display_name"]
    
    
@app.command("/random-reviewer")
def random_user_generator(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    random_users = get_random_reviewer(command["user_id"])
    if len(random_users) == 2:
        say(f"{name} Ваш ревьювер {random_users[0].name} и {random_users[1].name} 🤘")
    else:
        say(f"{name} Что-то пошло не так - напиши Гуле")


@app.command("/add_me_to_reviewers")
def random_user_generator(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    create_reviewer(command["user_id"], name)
    say(f"{name} Вы успешно добавлены как ревьювер")
    

# Main function
if __name__ == '__main__':
    app.start(port=int(os.environ.get("PORT", 80)))
