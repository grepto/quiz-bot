import glob
from random import randrange
import re
import logging

QUESTION_ROW_OFFSET = 1
ANSWER_ROW_OFFSET = 2
QUIZ_FILES_PATH = 'quiz/'


logger = logging.getLogger('quiz')


def get_clean_answer(answer):
    characters_to_replace = ['"', ',', '-', '\'', '\n', ':']
    answer = str(answer)
    answer = answer.lower()
    for character in characters_to_replace:
        answer = answer.replace(character, ' ')
    answer = re.sub(' +', ' ', answer)
    return answer.strip()


def get_quiz_content_from_file(quiz_file_path):
    with open(quiz_file_path, 'r', encoding='KOI8-R') as quiz_file:
        file_content = [row.strip() for row in quiz_file]
    quiz_content = []
    for row_index in range(len(file_content)):
        if file_content[row_index].split(' ')[0] == 'Вопрос':
            question_row_index = row_index + QUESTION_ROW_OFFSET
            question = ''
            while file_content[question_row_index] != '':
                question += file_content[question_row_index] + ' '
                question_row_index += 1
            answer = file_content[question_row_index + ANSWER_ROW_OFFSET]
            answer = re.split('[.(]+', answer)[0]
            answer = get_clean_answer(answer)
            quiz_content.append((question.strip(), answer.replace('"', '')))
    return quiz_content


def get_quiz_content():
    files = [file for file in glob.glob(QUIZ_FILES_PATH + '**/*.txt', recursive=True)]
    return [quiz_content for file in files for quiz_content in get_quiz_content_from_file(file)]


def get_random_question(quiz_content):
    question_id = randrange(0, len(quiz_content) - 1)
    logger.debug(f'{question_id} - {quiz_content[question_id][0]} - {quiz_content[question_id][1]}')
    return question_id, quiz_content[question_id][0]


def get_right_answer(quiz_content, question_id):
    return quiz_content[question_id][1]


def is_answer_correct(quiz_content, question_id, answer):
    return get_right_answer(quiz_content, question_id) == get_clean_answer(answer)


def main():
    quiz_content = get_quiz_content()
    print(get_random_question(quiz_content))


if __name__ == '__main__':
    main()
