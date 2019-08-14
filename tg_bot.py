import logging
import os

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
import telegram

from quiz_content import get_quiz_content, get_random_question, is_answer_correct, get_right_answer
from database import update_current_question, update_user_score, get_user_data

load_dotenv()
TG_TOKEN = os.getenv('TG_TOKEN')
TG_PROXY = os.getenv('TG_PROXY')

REQUEST_KWARGS = {
    'proxy_url': TG_PROXY,
}

logger = logging.getLogger('tg_bot')

quiz_content = get_quiz_content()
WAIT_FOR_CHOISE, WAIT_FOR_ANSWER = range(2)


def get_user_id(update):
    return f'user_tg_{update.message.from_user.id}'


def start_session(bot, update):
    user_id = get_user_id(update)
    user_score_delta = get_user_data(user_id)['score'] * -1
    update_user_score(user_id, user_score_delta)
    custom_keyboard = [['Начать викторину']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Привет! Я бот для викторин",
                     reply_markup=reply_markup)

    return WAIT_FOR_CHOISE


def get_help(bot, update):
    update.message.reply_text('Я бот для викторин. Нажимай кнопки, отвечай на вопросы, зарабатывай очки.')


def send_error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def send_question(bot, update):
    question_id, question = get_random_question(quiz_content)
    user_id = get_user_id(update)
    update_current_question(user_id, question_id)

    custom_keyboard = [['Сдаться']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text=question,
                     reply_markup=reply_markup)

    return WAIT_FOR_ANSWER


def send_right_answer(bot, update):
    user_id = get_user_id(update)
    question_id = get_user_data(user_id)['last_asked_question']
    answer = get_right_answer(quiz_content, question_id)

    custom_keyboard = [['Новый вопрос', 'Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text=f'Правильный ответ: {answer}',
                     reply_markup=reply_markup)
    return WAIT_FOR_CHOISE


def send_user_score(bot, update):
    user_id = get_user_id(update)
    score = get_user_data(user_id)['score']

    custom_keyboard = [['Новый вопрос']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text=f'Текущий счет: {score}',
                     reply_markup=reply_markup)

    return WAIT_FOR_CHOISE


def check_answer(bot, update):
    user_id = get_user_id(update)
    question_id = get_user_data(user_id)['last_asked_question']
    if is_answer_correct(quiz_content, question_id, update.message.text):
        reply_text = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        update_user_score(user_id, 1)
        custom_keyboard = [['Новый вопрос', 'Мой счет']]
        next_state = WAIT_FOR_CHOISE
    else:
        reply_text = 'Неправильно... Попробуешь ещё раз?'
        custom_keyboard = [['Сдаться']]
        next_state = WAIT_FOR_ANSWER

    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text=reply_text,
                     reply_markup=reply_markup)

    return next_state


def start_bot():
    logger.info(f'TG bot started')
    try:
        updater = Updater(TG_TOKEN, request_kwargs=REQUEST_KWARGS)

        dp = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start_session),
                          MessageHandler(Filters.text, start_session)],

            states={
                WAIT_FOR_CHOISE: [RegexHandler('^(Начать викторину|Новый вопрос)$', send_question),
                                  RegexHandler('^(Мой счет)$', send_user_score)],

                WAIT_FOR_ANSWER: [RegexHandler('^(Сдаться)$', send_right_answer),
                                  MessageHandler(Filters.text, check_answer)]
            },

            fallbacks=[CommandHandler('help', get_help)]
        )

        dp.add_handler(conv_handler)

        dp.add_error_handler(send_error)

        updater.start_polling()

        updater.idle()
    except Updater as err:
        logger.error(err)


if __name__ == '__main__':
    start_bot()
