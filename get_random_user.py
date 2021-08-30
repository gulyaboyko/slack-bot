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
        users.append(User(user_id.decode('utf-8'), "", group))
    return users

def get_all_reviwers():
    users = []
    for user_id in client.scan_iter():
        is_active = False
        if client.exists(user_id, "isActive"):
            is_active = (client.hget(user_id, "isActive") or "False".encode('utf-8')).decode('utf-8') == "True"
        is_real = client.exists(user_id, "name")
        group = ""
        if client.exists(user_id, "group"):
            group = client.hget(user_id, "group")
        if is_active & is_real:
            name = client.hget(user_id, "name").decode('utf-8')
            users.append(User(user_id.decode('utf-8'), name, group))
    return users


def get_current_user_group(current_user_id):
    group = ""
    for user_id in client.scan_iter():
        is_current = str(user_id.decode('utf-8')) == str(current_user_id)
        is_real = client.exists(current_user_id, "group")
        if is_real & is_current:
            group = client.hget(current_user_id, "group")
            return group
    return group


def create_reviewer(user_id, name, group):
    client.hset(user_id, 'name', name)
    client.hset(user_id, 'group', group)
    client.hset(user_id, 'isActive', "True")


def add_group(user_id, group):
    client.hset(user_id, 'group', group)


def mark_reviewer(user_id, is_active):
    global reviews
    client.hset(user_id, 'isActive', is_active)
    if is_active == "False":
        for review in reviews:
            if review.id == id:
                reviews.remove(review)


def get_random_reviewer(current_user_id, group):
    global reviews
    if not reviews:
        reviews = copy.deepcopy(get_all_reviwers())
    if not reviews:
        return []
    if len(get_all_reviwers()) <= 1:
        return []

    users = []
    other_group_reviewers = []
    the_same_group_reviewers = []
    secure_random = secrets.SystemRandom()
    if group == "":
        current_user_group = get_current_user_group(current_user_id)
    else:
        current_user_group = group
    print("current_user_group " + str(current_user_group))
    sys.stdout.flush()

    for review in reviews:
        if review.id != current_user_id:
            if review.group == current_user_group:
                the_same_group_reviewers.append(review)
            else:
                other_group_reviewers.append(review)

    if len(the_same_group_reviewers) == 0:
        # Или нет совсем людей из стрима, или уже были выбраны
        # и надо их взять во временный массив
        all_reviews = copy.deepcopy(get_all_reviwers())
        for review in all_reviews:
            if review.id != current_user_id:
                if review.group == current_user_group:
                    the_same_group_reviewers.append(review)

    if len(the_same_group_reviewers) == 0:
        # Нет из такого же стрима людей на проекте -> брать из 2 любых
        if len(other_group_reviewers) == 0:
            reviews = []
            reviews = copy.deepcopy(get_all_reviwers())
            for review in reviews:
                if review.id != current_user_id:
                    other_group_reviewers.append(review)
            users = secure_random.sample(other_group_reviewers, 2)
        elif len(other_group_reviewers) == 1:
            # Остался 1 не выбранный, но надо добавить еще 1
            first_user = other_group_reviewers[0]
            users = [first_user, get_second_reviewer(current_user_id, first_user.id)]
        else:
            users = secure_random.sample(other_group_reviewers, 2)
    else:
        the_same_group_reviewer = secure_random.sample(the_same_group_reviewers, 1)[0]
        if len(other_group_reviewers) == 0:
            other_group_reviewer = get_second_reviewer(current_user_id, the_same_group_reviewer.id)
        else:
            other_group_reviewer = secure_random.sample(other_group_reviewers, 1)[0]
        users = [the_same_group_reviewer, other_group_reviewer]

    if len(users) == 2:
        remove_reviewers(users[0].id, users[1].id)
        return users


def get_second_reviewer(current_user_id, first_reviewer_user_id):
    secure_random = secrets.SystemRandom()
    all_reviewers = copy.deepcopy(get_all_reviwers())
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
