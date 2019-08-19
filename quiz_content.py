import glob
from random import randrange
import re
import logging

QUIZ_FILES_PATH = 'quiz/'

logger = logging.getLogger('quiz')


def get_clean_answer(answer):
    characters_to_replace = ['"', ',', '-', '\'', '\n', ':', '.']
    answer = str(answer)
    answer = answer.lower()
    for character in characters_to_replace:
        answer = answer.replace(character, ' ')
    answer = re.sub(' +', ' ', answer)
    return answer.strip()


def prepare_quiz(quiz_raw_data):
    quiz_content = []
    quiz_raw_data_iter = iter(quiz_raw_data)
    while True:
        try:
            row = next(quiz_raw_data_iter)
        except StopIteration:
            break
        if row.split(' ')[0] == 'Вопрос':
            question = ''
            row = next(quiz_raw_data_iter)
            while row:
                question += row
                row = next(quiz_raw_data_iter)
            next(quiz_raw_data_iter)
            answer = next(quiz_raw_data_iter)
            quiz_content.append((question, get_clean_answer(answer)))
    return quiz_content


def get_quiz_content():
    files = [file for file in glob.glob(QUIZ_FILES_PATH + '**/*.txt', recursive=True)]
    quiz_content = []
    for file in files:
        with open(file, 'r', encoding='KOI8-R') as quiz_file:
            file_content = [row.strip() for row in quiz_file]
        quiz_content.extend(prepare_quiz(file_content))
    return quiz_content


def get_random_question(quiz_content):
    question_id = randrange(0, len(quiz_content) - 1)
    logger.debug(f'{question_id} - {quiz_content[question_id][0]} - {quiz_content[question_id][1]}')
    return question_id, quiz_content[question_id][0]


def get_right_answer(quiz_content, question_id):
    return quiz_content[question_id][1]


def is_answer_correct(quiz_content, question_id, answer):
    return get_right_answer(quiz_content, question_id) == get_clean_answer(answer)


def main():
    print(prepare_quiz([]))


if __name__ == '__main__':
    main()
