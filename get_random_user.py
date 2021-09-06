import copy
from user import User
import secrets
import redis
import os
import sys

reviews = []

REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL is None:
    client = redis.Redis()
else:
    client = redis.from_url(REDIS_URL)


def get_all_users():
    users = []
    for user_id in client.scan_iter():
        group = ""
        if client.exists(user_id, "group"):
            group = client.hget(user_id, "group")
        command = ""
        if client.exists(user_id, "command"):
            command = client.hget(user_id, "command")
        email = ""
        if client.exists(user_id, "email"):
            email = client.hget(user_id, "email")
        is_active = False
        if client.exists(user_id, "isActive"):
            is_active = client.hget(user_id, "isActive")
        users.append(User(user_id.decode('utf-8'), "", group, command, email, is_active))
    return users

def get_all_reviwers(current_comand):
    users = []
    for user_id in client.scan_iter():
        is_active = False
        if client.exists(user_id, "isActive"):
            is_active = (client.hget(user_id, "isActive") or "False".encode('utf-8')).decode('utf-8') == "True"
        group = ""
        if client.exists(user_id, "group"):
            group = client.hget(user_id, "group")
        command = ""
        if client.exists(user_id, "command"):
            command = client.hget(user_id, "command")
        email = ""
        if client.exists(user_id, "email"):
            email = client.hget(user_id, "email")
        the_same_command = str(current_comand) == str(command)
        if is_active & the_same_command:
            print("the_same_command current" + str(current_comand) + "another user command " + str(command))
            sys.stdout.flush()
            name = client.hget(user_id, "name").decode('utf-8')
            users.append(User(user_id.decode('utf-8'), name, group, command, email, True))
    return users


def get_current_user(current_user_id):
    for user_id in client.scan_iter():
        is_current = str(user_id.decode('utf-8')) == str(current_user_id)
        if is_current:
            group = ""
            if client.exists(current_user_id, "group"):
                group = client.hget(current_user_id, "group")
            command = ""
            if client.exists(current_user_id, "command"):
                command = client.hget(current_user_id, "command")
            email = ""
            if client.exists(current_user_id, "email"):
                email = client.hget(current_user_id, "email")
            is_active = False
            if client.exists(current_user_id, "isActive"):
                is_active = client.hget(current_user_id, "isActive")
            return User(current_user_id, "", group, command, email, is_active)


def create_reviewer(user_id, name, group, command, email):
    client.hset(user_id, 'name', name)
    client.hset(user_id, 'group', group)
    client.hset(user_id, 'command', command)
    client.hset(user_id, 'email', email)
    client.hset(user_id, 'isActive', "True")


def add_group(user_id, group):
    client.hset(user_id, 'group', group)


def add_to_command(user_id, command):
    client.hset(user_id, 'command', command)


def mark_reviewer(user_id, is_active):
    global reviews
    client.hset(user_id, 'isActive', is_active)
    if is_active == "False":
        for review in reviews:
            if review.id == id:
                reviews.remove(review)


def get_random_reviewer(current_user_id):
    global reviews

    current_user = get_current_user(current_user_id)

    current_user_group = current_user.group

    print("user id " + str(current_user.id) + "user group " +
          str(current_user.group) + " " +
          str(current_user.command))
    sys.stdout.flush()

    if not reviews:
        reviews = copy.deepcopy(get_all_reviwers(current_user.command))
    if not reviews:
        return []
    if len(get_all_reviwers(current_user.command)) <= 1:
        return []

    users = []
    other_group_reviewers = []
    the_same_group_reviewers = []
    secure_random = secrets.SystemRandom()

    for review in reviews:
        if review.id != current_user_id:
            if review.group == current_user_group:
                the_same_group_reviewers.append(review)
            else:
                other_group_reviewers.append(review)

    if len(the_same_group_reviewers) == 0:
        # Или нет совсем людей из стрима, или уже были выбраны
        # и надо их взять во временный массив
        all_reviews = copy.deepcopy(get_all_reviwers(current_user.command))
        for review in all_reviews:
            if review.id != current_user_id:
                the_same_group = review.group == current_user_group
                if the_same_group:
                    the_same_group_reviewers.append(review)

    if len(the_same_group_reviewers) == 0:
        # Нет из такого же стрима людей на проекте -> брать из 2 любых
        if len(other_group_reviewers) == 0:
            reviews = []
            reviews = copy.deepcopy(get_all_reviwers(current_user.command))
            for review in reviews:
                if review.id != current_user_id:
                    other_group_reviewers.append(review)
            users = secure_random.sample(other_group_reviewers, 2)
        elif len(other_group_reviewers) == 1:
            # Остался 1 не выбранный, но надо добавить еще 1
            first_user = other_group_reviewers[0]
            users = [first_user, get_second_reviewer(current_user_id, first_user.id, current_user.command)]
        else:
            users = secure_random.sample(other_group_reviewers, 2)
    else:
        the_same_group_reviewer = secure_random.sample(the_same_group_reviewers, 1)[0]
        if len(other_group_reviewers) == 0:
            other_group_reviewer = get_second_reviewer(current_user_id, the_same_group_reviewer.id, current_user.command)
        else:
            other_group_reviewer = secure_random.sample(other_group_reviewers, 1)[0]
        users = [the_same_group_reviewer, other_group_reviewer]

    if len(users) == 2:
        remove_reviewers(users[0].id, users[1].id)
        return users


def get_second_reviewer(current_user_id, first_reviewer_user_id, current_user_command):
    secure_random = secrets.SystemRandom()
    all_reviewers = copy.deepcopy(get_all_reviwers(current_user_command))
    _reviewers = []
    for review in all_reviewers:
        if review.id != current_user_id and review.id != first_reviewer_user_id:
            _reviewers.append(review)
    return secure_random.sample(_reviewers, 1)[0]


def remove_reviewers(id1, id2):
    global reviews
    remove_items = []
    for review in reviews:
        if review.id == id1 or review.id == id2:
            remove_items.append(review)
    for remove_item in remove_items:
        reviews.remove(remove_item)
