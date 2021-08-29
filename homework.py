import os
import time
import requests
import telegram
import logging
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
bot = telegram.Bot(token=TELEGRAM_TOKEN)
URL = 'https://praktikum.yandex.ru/'
# Новый мехзанизм отслеживания статуса последней домашки
# Становится Верным, только при условии, что последняя работа
# была успешно зачтена
last_hw_checked = False


def parse_homework_status(homework):
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
    global last_hw_checked
    logging.debug('Бот был запущен')
    timestamp = 0
    while True:
        try:
            # парсим только в случае если есть текущая домашка не проверена
            while last_hw_checked is False:
                homeworks = get_homeworks(int(timestamp))
                homework = homeworks['homeworks'][0]
                if (homework['status'] != 'reviewing'):
                    if (homework['status'] == 'approved'):
                        last_hw_checked = True
                    else:
                        last_hw_checked = False
                    text = parse_homework_status(homework)
                    send_message(text)
                time.sleep(5 * 60)  # Опрашивать раз в пять минут
        except Exception as e:
            text = f'Бот упал с ошибкой: {e}'
            logging.error(text)
            send_message(text)
            time.sleep(5)


if __name__ == '__main__':
    main()
