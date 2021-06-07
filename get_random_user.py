import copy
from user import User
import secrets
import redis
import os
from urllib.parse import urlparse

reviews = []

REDIS_URL = os.environ.get("REDIS_URL")
if REDIS_URL is None:
    client = redis.Redis()
else:
    url = urlparse(REDIS_URL)
    client = redis.Redis(host=url.hostname, port=url.port, username=url.username, password=url.password, ssl=True, ssl_cert_reqs=None)

def get_all_reviwers():
    users = []
    for user_id in client.scan_iter():
        is_active = client.hget(user_id, "isActive").decode('utf-8') == "True"
        if is_active:
            users.append(User(user_id.decode('utf-8'), client.hget(user_id, "name")))
    return users


def create_reviewer(user_id, name):
    client.hset(user_id, 'name', name)
    client.hset(user_id, 'isActive', "True")


def mark_reviewer(user_id, is_active):
    global reviews
    client.hset(user_id, 'isActive', is_active)
    if bool == 0:
        for review in reviews:
            if review.id == id:
                reviews.remove(review)


def get_random_reviewer(excluded_id1):
    global reviews
    if not reviews:
        reviews = copy.deepcopy(get_all_reviwers())
    if not reviews:
        return []
    if len(get_all_reviwers()) <= 1:
        return []

    users = []
    _reviewers = []
    secure_random = secrets.SystemRandom()
    for review in reviews:
        if review.id != excluded_id1:
            _reviewers.append(review)
    if len(_reviewers) == 0:
        # Когда или изначально массив уже весь перевыбран
        # или остался 1 и это тот кто запрашивает себе ревьювера
        reviews = []
        reviews = copy.deepcopy(get_all_reviwers())
        for review in reviews:
            if review.id != excluded_id1:
                _reviewers.append(review)
        users = secure_random.sample(_reviewers, 2)
    elif len(_reviewers) == 1:
        first_user = _reviewers[0]
        reviews = []
        reviews = copy.deepcopy(get_all_reviwers())
        _reviewers = []
        for review in reviews:
            if review.id != excluded_id1 and review.id != first_user.id:
                _reviewers.append(review)
        users = [first_user, secure_random.sample(_reviewers, 1)[0]]
    elif len(_reviewers) == 2:
        # Возвращаем 2
        users = _reviewers
    elif len(_reviewers) > 2:
        # Возвращаем любых 2
        users = secure_random.sample(_reviewers, 2)

    if len(users) == 2:
        remove_reviewers(users[0].id, users[1].id)
        return users


def remove_reviewers(id1, id2):
    global reviews
    remove_items = []
    for review in reviews:
        if review.id == id1 or review.id == id2:
            remove_items.append(review)
    for remove_item in remove_items:
        reviews.remove(remove_item)
