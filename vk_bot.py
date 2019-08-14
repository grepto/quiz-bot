import os
import random
import logging

from dotenv import load_dotenv
import vk_api
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType

from quiz_content import get_quiz_content, get_random_question, is_answer_correct, get_right_answer
from database import update_current_question, update_user_score, get_user_data

load_dotenv()
VK_GROUP_TOKEN = os.getenv('VK_GROUP_TOKEN')

quiz_content = get_quiz_content()

logger = logging.getLogger('vk_bot')

def echo(event, vk_api):
    keyboard = get_message_keyboard(['Новый вопрос', 'Сдаться', 'Мой счет'])
    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        message=event.text,
        random_id=random.randint(1, 1000)
    )


def get_user_id(event):
    return f'user_vk_{event.user_id}'


def get_message_keyboard(buttons):
    all_buttons = {
        'Начать викторину': 'primary',
        'Новый вопрос': 'primary',
        'Сдаться': 'negative',
        'Мой счет': 'default',
    }
    keyboard = VkKeyboard(one_time=True)
    for button in buttons:
        keyboard.add_button(button, color=all_buttons.get(button, 'default'))
    return keyboard


def start_game(event, vk_api):
    user_id = get_user_id(event)
    user_score_delta = get_user_data(user_id)['score'] * -1
    update_user_score(user_id, user_score_delta)
    keyboard = get_message_keyboard(['Начать викторину'])
    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        message='Привет! Я бот для викторин',
        random_id=random.randint(1, 1000)
    )


def send_question(event, vk_api):
    question_id, question = get_random_question(quiz_content)
    user_id = get_user_id(event)
    update_current_question(user_id, question_id)
    keyboard = get_message_keyboard(['Сдаться'])
    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        message=question,
        random_id=random.randint(1, 1000)
    )


def send_right_answer(event, vk_api):
    user_id = get_user_id(event)
    question_id = get_user_data(user_id)['last_asked_question']
    answer = get_right_answer(quiz_content, question_id)
    keyboard = get_message_keyboard(['Новый вопрос', 'Мой счет'])
    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        message=f'Правильный ответ {answer}',
        random_id=random.randint(1, 1000)
    )


def send_user_score(event, vk_api):
    user_id = get_user_id(event)
    score = get_user_data(user_id)['score']
    keyboard = get_message_keyboard(['Новый вопрос'])
    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        message=f'Текущий счет: {score}',
        random_id=random.randint(1, 1000)
    )


def check_answer(event, vk_api):
    user_id = get_user_id(event)
    question_id = get_user_data(user_id)['last_asked_question']
    if is_answer_correct(quiz_content, question_id, event.text):
        reply_text = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        update_user_score(user_id, 1)
        keyboard = get_message_keyboard(['Новый вопрос', 'Мой счет'])

    else:
        reply_text = 'Неправильно... Попробуешь ещё раз?'
        keyboard = get_message_keyboard(['Сдаться'])

    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        message=reply_text,
        random_id=random.randint(1, 1000)
    )


def start_bot():
    logger.info('VK bot started')
    try:
        vk_session = vk_api.VkApi(token=VK_GROUP_TOKEN)
        api = vk_session.get_api()
        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.text == 'Начать':
                    start_game(event, api)
                elif event.text in ('Новый вопрос', 'Начать викторину'):
                    send_question(event, api)
                elif event.text == 'Сдаться':
                    send_right_answer(event, api)
                elif event.text == 'Мой счет':
                    send_user_score(event, api)
                else:
                    check_answer(event, api)
    except vk_api.exceptions.ApiError as error:
        logger.error(error)


if __name__ == '__main__':
    start_bot()
