import os
import time
import datetime
import requests
import telegram
import logging
import sys
from dotenv import load_dotenv

homeworks = {}
load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s'
)
PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# проинициализируйте бота здесь,
# чтобы он был доступен в каждом нижеобъявленном методе,
# и не нужно было прокидывать его в каждый вызов
bot = telegram.Bot(token=TELEGRAM_TOKEN)
url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    status = homework['status']
    if (homework_name not in homeworks.keys()):
        homeworks[homework_name] = status
    if (status == 'rejected'):
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif (status == 'approved'):
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    else:
        return (logging.info('Работа пока не проверена'))
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    homework_statuses = requests.get(url, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    logging.info('Отправлено сообщение')
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    logging.debug('Бот был запущен')
    # случайная дата, с начала которой домашек не сдавалось
    date = datetime.date(year=2020, month=8, day=23)
    timestamp = time.mktime(date.timetuple())  # Начальное значение timestamp
    while True:
        try:
            homeworks = get_homeworks(int(timestamp))
            if (homeworks['homeworks']):
                homework = homeworks['homeworks'][0]
                if (homework['status'] != 'reviewing'):
                    text = parse_homework_status(homework)
                    send_message(text)
                    sys.exit()
            else:
                logging.info('Домашек.нет')
            time.sleep(5 * 60)  # Опрашивать раз в пять минут
        except Exception as e:
            text = f'Бот упал с ошибкой: {e}'
            logging.error(text)
            send_message(text)
            time.sleep(5)


if __name__ == '__main__':
    main()
