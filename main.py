from get_random_user import get_random_reviewer, create_reviewer, mark_reviewer, add_group, get_all_reviwers, get_all_users
from user import User
import os
# Use the package we installed
from slack_bolt import App
from slack_sdk import WebClient
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
import sys

# Slack bolt - wtf
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN", ""),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET", "")
)

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN", ""))


def get_user_info(user_id):
    result = client.users_info(user=user_id)
    return result["user"]["profile"]["display_name"]

def get_user_info_by_login(user_login):
    result = client.users_list()
    for user in result["members"]:
        print(user)
        # Key user info on their unique user ID
        # user_id = user["id"]
        # # Store the entire user object (you may not need all of the info)
        # users_store[user_id] = user


@app.command("/random-reviewer")
def random_user_generator(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    group = ""
    if "text" in command:
        group = command["text"].casefold().strip()
    print("user id " + str(group))
    sys.stdout.flush()
    random_users = get_random_reviewer(command["user_id"], group)
    if len(random_users) == 2:
        say(f"{name} Ваш ревьювер <@{random_users[0].id}> и <@{random_users[1].id}> 🤘")
    else:
        say(f"{name} Что-то пошло не так - напиши Гуле")


@app.command("/all_users")
def all_users(ack, say, command):
    ack()
    users = get_all_users()
    for user in users:
        say(f"<@{user.id}> в стриме {user.group}")


@app.command("/add_me_to_reviewers")
def random_user_generator(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    group = command["text"].casefold().strip()
    create_reviewer(command["user_id"], name, group)
    say(f"{name} Вы успешно добавлены как ревьювер")


@app.command("/on_vacation")
def on_vacation(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    mark_reviewer(command["user_id"], "False")
    say(f"{name} Вы успешно временно удалены из ревьюверов")


@app.command("/add_group")
def on_vacation(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    group = command["text"].casefold().strip()
    add_group(command["user_id"], group)
    say(f"{name} Вы успешно добавлены в стрим {group}")


@app.command("/returned_from_vacation")
def returned_from_vacation(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    mark_reviewer(command["user_id"], "True")
    say(f"{name} Вы успешно вернулись в ревьюверы")


flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    # handler runs App's dispatch method
    return handler.handle(request)

@flask_app.route("/users", methods=["GET"])
def users():
    users = get_all_reviwers()
    for user in users:
        print("user id " + str(user.id) + "user name " + str(user.name) + "user group " + str(user.group))
        sys.stdout.flush()
    return "OK"


@flask_app.route("/back_vacation", methods=["GET"])
def back_vacation():
    mark_reviewer("UFJ68B63H", "True")
    return "OK"


