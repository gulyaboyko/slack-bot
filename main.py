from get_random_user import get_random_reviewer, create_reviewer, mark_reviewer, get_all_reviwers
from user import User
import os
# Use the package we installed
from slack_bolt import App
from slack_sdk import WebClient
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler

# Slack bolt - wtf
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN", ""),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET", "")
)

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN", ""))


def get_user_info(user_id):
    result = client.users_info(user=user_id)
    return result["user"]["profile"]["display_name"]


@app.command("/random-reviewer")
def random_user_generator(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    random_users = get_random_reviewer(command["user_id"])
    if len(random_users) == 2:
        say(f"{name} Ваш ревьювер @{random_users[0].name} и @{random_users[1].name} 🤘")
    else:
        say(f"{name} Что-то пошло не так - напиши Гуле")


@app.command("/add_me_to_reviewers")
def random_user_generator(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    create_reviewer(command["user_id"], name)
    say(f"{name} Вы успешно добавлены как ревьювер")


@app.command("/on_vacation")
def on_vacation(ack, say, command):
    ack()
    name = get_user_info(command["user_id"])
    mark_reviewer(command["user_id"], "False")
    say(f"{name} Вы успешно временно удалены из ревьюверов")


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

# Main function
# if __name__ == '__main__':


@flask_app.route("/init", methods=["GET"])
def add_users():
    create_reviewer("U01G45LR2BA", "Валерий Безуглый")
    create_reviewer("U01V2JK6YE5", "Turalin Arman")
    create_reviewer("U01QJ7BDQHE", "Vladimir Boyko")
    create_reviewer("U01ASCDRBP0", "Сергей Мустафаев")
    create_reviewer("UFJ68B63H", "Roman Aleksandrov")
    create_reviewer("U01AVKUKECC", "Vladislav Lisianskii")
    create_reviewer("U015ZQ9QRC7", "Evgeny Kapanov")
    create_reviewer("U01DRQFPB8X", "Nikita Tepliakov")
    create_reviewer("UFGGE710R", "Denis Smirnov")
    return "OK"


@flask_app.route("/vacation", methods=["GET"])
def vacation():
    mark_reviewer("UFJ68B63H", "False")
    return "OK"


@flask_app.route("/back_vacation", methods=["GET"])
def back_vacation():
    mark_reviewer("UFJ68B63H", "True")
    return "OK"


@flask_app.route("/all_users", methods=["GET"])
def all_users():
    reviews = get_all_reviwers
    users = ""
    for user in reviews:
        users += " " + user.name
    return users

