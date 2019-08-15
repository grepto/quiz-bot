import json
import os

import redis
from dotenv import load_dotenv

load_dotenv()
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASWORD = os.getenv('REDIS_PASWORD')

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASWORD,
    charset="utf-8",
    decode_responses=True)


def update_user_data(user_id, user_data):
    r.set(user_id, json.dumps(user_data))


def get_user_data(user_id):
    default_user_data = {
        'last_asked_question': None,
        'score': 0
    }
    user_data = r.get(user_id)
    return json.loads(user_data) if user_data else default_user_data


def update_current_question(user_id, question_id):
    user_data = get_user_data(user_id)
    user_data['last_asked_question'] = question_id
    update_user_data(user_id, user_data)


def update_user_score(user_id, delta=1):
    user_data = get_user_data(user_id)
    user_data['score'] = user_data.get('score', 0) + delta
    update_user_data(user_id, user_data)


def main():
    pass


if __name__ == '__main__':
    main()
