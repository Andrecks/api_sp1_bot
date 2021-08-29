import os
import time
import requests
import telegram
import logging
from dotenv import load_dotenv

verdicts = {'approved': ['Ревьюеру всё понравилось, работа зачтена!', True],
            'rejected': ['К сожалению, в работе нашлись ошибки.', True],
            'reviewing': ['Работу проверяют', False]
            }
load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)
PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = telegram.Bot(token=TELEGRAM_TOKEN)
URL = 'https://praktikum.yandex.ru/'
# Новый мехзанизм отслеживания статуса последней домашки
# Становится Верным, только при условии, что последняя работа
# была успешно зачтена
last_hw_checked = False


def parse_homework_status(homework):
    global last_hw_checked
    if ({'status', 'homework_name'} >= homework.keys()):
        raise KeyError('Нужные данные не найдены в ответе')
    homework_name = homework['homework_name']
    status = homework['status']
    if ((status not in verdicts.keys())):
        raise KeyError('Неизвестный статус проверки')
    last_hw_checked = verdicts[status][1]
    return (f'У вас проверили работу "{homework_name}"!'
            f'\n\n{verdicts[status][0]}')


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    url_add = 'api/user_api/homework_statuses/'
    homework_statuses = requests.get(URL + url_add,
                                     headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    logging.info('Отправлено сообщение')
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    global last_hw_checked
    logging.debug('Бот был запущен')
    timestamp = 0
    while True:
        try:
            homeworks = get_homeworks(int(timestamp))
            homework = homeworks['homeworks'][0]
            text = parse_homework_status(homework)
            # Отправляем сообщение только в случае, если дз проверено
            if (last_hw_checked is True):
                send_message(text)
            time.sleep(5 * 60)  # Опрашивать раз в пять минут
        except Exception as e:
            text = f'Бот упал с ошибкой: {e}'
            logging.error(text)
            send_message(text)
            time.sleep(5)


if __name__ == '__main__':
    main()
