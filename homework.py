from dotenv import load_dotenv
import telegram
import time
import requests
from http import HTTPStatus
import exceptions
import os
import logging
import sys

load_dotenv()


PRACTICUM_TOKEN = os.getenv('TOKEN')
TELEGRAM_TOKEN = os.getenv('T_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CH_ID')

RETRY_TIME = 1
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Sends message."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.NetworkError:
        raise exceptions.BotNotSendingStuff


def get_api_answer(current_timestamp):
    """Gets api answer."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception:
        raise exceptions.ApiUnreachable(ENDPOINT)
    if response.status_code != HTTPStatus.OK:
        raise exceptions.Not200StatusCodeResponse
    return response.json()


def check_response(response):
    """Checks response."""
    if not isinstance(response, dict):
        raise TypeError
    if ('homeworks' not in response
            or not isinstance(response['homeworks'], list)):
        raise KeyError('The response differs from the expected one.')
    return response['homeworks']


def parse_status(homework):
    """Parses status."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Checks_tokens."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def get_logger():
    """Creates logger."""
    logger = logging.getLogger(__name__)

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s, [%(levelname)s] %(message)s')

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(level=logging.DEBUG)
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger


def main():
    """Основная логика работы бота."""
    logger = get_logger()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    last_msg_st = ''
    last_msg_er = ''
    ...

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if homework:
                msg = parse_status(homework[0])
                if not msg == last_msg_st:
                    logger.info(f'Attempting to send a tg msg {msg}')
                    send_message(bot, msg)
                    last_msg_st = msg
            else:
                logger.debug('Отсутствие в ответе новых статусов')
            current_timestamp = response['current_date']
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if not message == last_msg_er:
                send_message(bot, message)
                last_msg_er = message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
