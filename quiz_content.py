import glob
from random import randrange
import re
import logging
from itertools import takewhile

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
    for row in quiz_raw_data_iter:
        if row.startswith('Вопрос '):
            question = ' '.join(list(takewhile(lambda x: x, quiz_raw_data_iter)))
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
    raw_quiz = ['Чемпионат:', 'Чемпионат Екатеринбурга - 2011', '', 'Дата:', '12-Nov-2011', '', 'Тур:',
                '1 тур. "Самум"',
                '', 'Инфо:', 'Команда благодарит Наталью Тарасову, команду "Большая Красная П"',
                '(Пермь), Алексея Самсонова и Татьяну Веремеенко, а также Даниила',
                'Пахомова, Романа Немучинского, Александра Либера и команду "Игры разума"',
                '(Ростов-на-Дону) за ценные замечания.', '', 'Вопрос 1:',
                'Злодей из пакистанского фильма 1990 года подвергает героев особой пытке',
                '- заставляет прослушивать аудиозапись своих произведений. Назовите', 'фамилию этого злодея.', '',
                'Ответ:',
                'Рушди.', '', 'Комментарий:', 'Фильм снят вскоре после того, как Рушди был проклят аятоллой Хомейни.',
                'Разумеется, персонаж фильма - это просто исчадие ада. Надеемся, чтение',
                'вопросов этого пакета не станет для вас пыткой.', '', 'Источник:',
                '1. http://www.imdb.com/title/tt0251144/', '2. http://en.wikipedia.org/wiki/International_Guerillas',
                '',
                'Автор:', 'Илья Аввакумов (Екатеринбург)', '', 'Вопрос 2:',
                'Он родился в 1828 году. Закончил институт с отличием, преуспел в научной',
                'деятельности, имел множество публикаций. Однако в русском языке его',
                'фамилия стала обозначать человека, не блещущего умственными', 'способностями. Назовите эту фамилию.',
                '',
                'Ответ:', 'Даун.', '', 'Комментарий:', 'Джон Даун впервые описал "синдром Дауна".', '', 'Источник:',
                'http://ru.wikipedia.org/wiki/Даун,_Джон', '', 'Автор:', 'Илья Аввакумов (Екатеринбург)', '',
                'Вопрос 3:',
                '<раздатка>', 'Одним из горячо обсуждаемых вопросов была проблема смешанных',
                'еврейско-арабских браков.',
                '</раздатка>', 'Перед вами цитата из статьи Википедии о конференции, состоявшейся в',
                'середине XX века. Какие две буквы мы заменили в этой цитате?', '', 'Ответ:', 'ий.', '', 'Комментарий:',
                'Еврейско-арийские браки препятствовали окончательному решению еврейского', 'вопроса.', '', 'Источник:',
                'http://ru.wikipedia.org/wiki/Ванзейская_конференция', '', 'Автор:', 'Илья Аввакумов (Екатеринбург)',
                '',
                'Вопрос 4:', 'В советском мультфильме 1979 года усатый человек поднимает с земли',
                'предмет, который много веков пролежал в забвении. Назовите фамилию этого', 'человека.', '', 'Ответ:',
                'Кубертен.', '', 'Комментарий:',
                'Мультфильм снят перед Олимпиадой-80. Кубертен символично поднимает факел',
                'и возрождает олимпийское движение.', '', 'Источник:', 'Мультфильм "Большая эстафета" (1979).',
                'http://www.youtube.com/watch?v=ZsHA5mKqBbY&t=5m01s', '', 'Автор:', 'Илья Аввакумов (Екатеринбург)', '']
    print(prepare_quiz(raw_quiz))


if __name__ == '__main__':
    main()
