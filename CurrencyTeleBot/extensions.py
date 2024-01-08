"""Данный код реализует простейшего телеграмм бота по обработке запросов от пользователя в установленном
формате: валюта1 валюта2 сумма, и возвращает текущий актуальный обменный курс с указанием валют в
международном формате. Дополнительно происходит обработка ошибок ввода от пользователя с выводом комментариев и
технических ошибок, принятых согласно документации сайта.
Применяется API с ресурса  https://www.exchangerate-api.com/
В данном варианте коде осуществлено разделение функционала на 4 класса: Исключения, Выполнение API запроса и
обработка результатов, Работа бота с пользователем, включая обработку команд и вывод результатов, отдельный
класс для инициализации и запуска телеграм-бота. В другом файле (extensions2.py) представлен иной подход.
Хотя код в другом файле реализован более компактно, на мой взгляд, данный вариант более подходит для дальнейшего
развития бота с добавлением функционала"""


import requests
from config import CURRENCY_TOKEN, api_key
import telebot

CODES = {'доллар': 'USD', 'гривна': 'UAH',  # Словарь для соответствия названия валют и их кодов
         'евро': 'EUR', 'франк': 'CHF',
         'теньге': 'KZT', 'спецправа': 'XDR',
         'йена': 'JPY', 'шекель': 'ILS',
         'фунт': 'GBP', 'юань': 'CNY',
         'рубль': 'RUB', 'дирхам': 'AED'}  # Добавьте другие валюты по мере необходимости


class APIException(Exception):
    """Исключение для обработки ошибок API"""
    pass


class CurrencyConverter:
    """Класс для конвертации валют с использованием API"""
    @staticmethod
    def get_available_currencies() -> list:
        """Возвращает список доступных валют"""
        return list(CODES.keys())

    @staticmethod
    def get_price(base: str, quote: str, amount: float) -> float:
        """Возвращает стоимость указанной суммы одной валюты в другую"""
        url = f'https://v6.exchangerate-api.com/v6/{api_key}/pair/{base}/{quote}'  # адрес API ресурса
        r = requests.get(url)  # создание GET запроса через библиотеку
        data = r.json()  # обработка ответа в формат JSON

        if data['result'] == 'error':  # Проверяем успешность ответа от API
            error_type = data.get('error-type', 'unknown')
            error_message = f"API Error: {error_type}"

            error_messages = {  # Сопоставляем тип ошибки с соответствующим сообщением
                'unsupported-code': 'Unsupported currency code',
                'malformed-request': 'Malformed request',
                'invalid-key': 'Invalid API key',
                'inactive-account': 'Inactive account (email not confirmed)',
                'quota-reached': 'Quota reached (maximum number of requests exceeded)'}

            # Получаем сообщение об ошибке из словаря, или используем 'unknown', если тип ошибки неизвестен
            error_message += f" - {error_messages.get(error_type, 'unknown')}"
            raise APIException(error_message)
        # Проверяем, что указанная валюта для конвертации присутствует в ответе
        if 'conversion_rate' not in data:
            raise APIException(f"Failed to get conversion rate for {base}/{quote}")

        try:
            # Попытка получить курс валюты из ответа
            rate = data['conversion_rate']
        except KeyError:
            raise APIException(f"Failed to get conversion rate from the response")
        # Вычисляем стоимость валюты, умножив курс на количество
        result = amount * rate
        return result


class TelegramBot:
    """Класс для работы с телеграм-ботом"""
    @staticmethod
    def start(bot: telebot.TeleBot, message: telebot.types.Message) -> None:
        """Обработчик команды /start"""
        bot.send_message(message.chat.id, "Привет! Я бот для конвертации валют. \
                         \nПример ввода запроса: доллар рубль 100 \
                         \nИспользуйте команды /help или /values для получения информации.")

    @staticmethod
    def help(bot: telebot.TeleBot, message: telebot.types.Message) -> None:
        """Обработчик команды /help"""
        bot.send_message(message.chat.id, "Используйте команды:\n/values - \
получить информацию о доступных валютах\nвалюта1 валюта2 \
количество. пример: доллар рубль 100")

    @staticmethod
    def values(bot: telebot.TeleBot, message: telebot.types.Message) -> None:
        """Обработчик команды /values"""
        available_currencies = CurrencyConverter.get_available_currencies()
        currencies_text = f'Доступные валюты: {", ".join(available_currencies)}'
        bot.send_message(message.chat.id, currencies_text)

    @staticmethod
    def convert(bot: telebot.TeleBot, message: telebot.types.Message) -> None:
        """Обработчик команды от пользователя и конвертации валют"""
        try:
            command = message.text.lower().split()  # обработка запроса не зависимо от регистра с разделением
            if len(command) != 3:  # проверка на корректность формата запроса по количеству
                raise APIException("Неверный формат команды. Введите: валюта1 валюта2 количество")

            base_currency, quote_currency, amount = command  # инициализация сведений из команды
            base_currency = CODES.get(base_currency)  # сопоставление названия валюты коду
            quote_currency = CODES.get(quote_currency)  # сопоставление названия валюты коду

            try:
                amount = float(amount)  # проверка на корректность суммы
            except ValueError:
                raise APIException(f'Некорректно введена сумма: {amount}')

            if base_currency is None or quote_currency is None:  # проверка на доступность валюты
                raise APIException("Неподдерживаемая валюта")

            if base_currency == quote_currency:  # проверка на возможность конвертации
                raise APIException("Нельзя конвертировать одну и ту же валюту")

            result = (CurrencyConverter.get_price(base_currency, quote_currency, amount))  # вызов метода запроса
            result_message = f"Стоимость {amount} {base_currency} составляет: {round(result, 2)} {quote_currency}"
            # вывод результатов запроса в читаемом формате
            bot.send_message(message.chat.id, result_message)  # отправка сообщения пользователю
        except APIException as e:  # вызов исключения с ошибкой пользователя
            bot.send_message(message.chat.id, f"Ошибка пользователя: {str(e)}")
        except Exception as e:  # вызов исключения с технической ошибкой от сервиса
            bot.send_message(message.chat.id, f"Технический сбой: {str(e)}")


class CurrencyConverterBot:
    """Класс для инициализации и запуска телеграм-бота"""
    def __init__(self, token: str) -> None:
        self.bot = telebot.TeleBot(token)

        @self.bot.message_handler(commands=['start'])
        def handle_start(message) -> None:
            TelegramBot.start(self.bot, message)

        @self.bot.message_handler(commands=['help'])
        def handle_help(message) -> None:
            TelegramBot.help(self.bot, message)

        @self.bot.message_handler(commands=['values'])
        def handle_values(message) -> None:
            TelegramBot.values(self.bot, message)

        @self.bot.message_handler(func=lambda message: True)
        def handle_convert(message) -> None:
            TelegramBot.convert(self.bot, message)

    def run(self) -> None:
        """Запуск телеграм-бота"""
        self.bot.polling(none_stop=True)


if __name__ == '__main__':
    bot_main = CurrencyConverterBot(CURRENCY_TOKEN)  # создание объекта бот, установленного класса
    bot_main.run()  # запуск объекта в работу
