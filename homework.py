import os
import time
import requests
import telegram
import logging
import sys
from dotenv import load_dotenv

verdicts = {'approved': 'Ревьюеру всё понравилось, работа зачтена!',
            'rejected': 'К сожалению, в работе нашлись ошибки.',
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
# Переменная для подсчета успешно сданных домашек.
hw_count = int(os.getenv('COUNTER'))
# проинициализируйте бота здесь,
# чтобы он был доступен в каждом нижеобъявленном методе,
# и не нужно было прокидывать его в каждый вызов
bot = telegram.Bot(token=TELEGRAM_TOKEN)
URL = 'https://praktikum.yandex.ru/'

# на данный момент проверенных там 5.


def parse_homework_status(homework):
    global hw_count
    homework_name = homework['homework_name']
    status = homework['status']
    if status in verdicts.keys():
        return (f'У вас проверили работу "{homework_name}"!'
                f'\n\n{verdicts[status]}')
    else:
        raise KeyError('Неизвестный статус проверки')


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
    global hw_count
    logging.debug('Бот был запущен')
    # date = datetime.date(year=2020, month=8, day=23)
    timestamp = 0  # time.mktime(date.timetuple())
    while True:
        try:
            homeworks = get_homeworks(int(timestamp))
            # парсим только в случае если есть домашки, которые не прошли ревью
            if (len(homeworks['homeworks']) > hw_count):
                homework = homeworks['homeworks'][0]
                if (homework['status'] != 'reviewing'):
                    if (homework['status'] == 'approved'):
                        os.environ['COUNTER'] = hw_count + 1
                    text = parse_homework_status(homework)
                    send_message(text)
                    sys.exit()
            time.sleep(5 * 60)  # Опрашивать раз в пять минут
        except Exception as e:
            text = f'Бот упал с ошибкой: {e}'
            logging.error(text)
            send_message(text)
            time.sleep(5)


if __name__ == '__main__':
    main()
