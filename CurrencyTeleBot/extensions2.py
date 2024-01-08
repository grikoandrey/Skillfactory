"""Данный код реализует простейшего телеграмм бота по обработке запросов от пользователя в установленном
формате: валюта1 валюта2 сумма, и возвращает текущий актуальный обменный курс с указанием валют в
международном формате. Дополнительно происходит обработка ошибок ввода от пользователя с выводом комментариев и
технических ошибок, принятых согласно документации сайта.
Применяется API с ресурса  https://www.exchangerate-api.com/
В данном варианте коде осуществлено разделение функционала на 2 класса: Исключения, Общий класс: по
выполнению API запроса, обработки результатов, работа бота с пользователем, включая обработку команд и
вывод результатов, инициализацию и запуска телеграм-бота. В другом файле (extensions.py) представлен иной подход.
Хотя код в другом файле реализован менее компактно, но более структурировано разделен на функционал, на мой взгляд,
данный вариант более подходит для конечного готового продукта без добавления функционала"""


import requests  # импортируем библиотеку для обработки запросов
import telebot  # импортируем библиотеку для создания бота
from config2 import CURRENCY_TOKEN, api_key  # импортируем приватные данные из файла


CODES = {'доллар': 'USD', 'гривна': 'UAH',  # создание константного словаря используемых валют в формате
         'евро': 'EUR', 'франк': 'CHF',  # ходовое название валюты: код валюты, установленный стандартом для запроса
         'теньге': 'KZT', 'спецправа': 'XDR',
         'йена': 'JPY', 'шекель': 'ILS',
         'фунт': 'GBP', 'юань': 'CNY',
         'рубль': 'RUB', 'дирхам': 'AED'}  # возможно добавление любой валюты в аналогичном формате


class APIException(Exception):  # создание собственного класса вызываемых исключений
    pass


class CurrencyConverterBot:
    def __init__(self, token: str) -> None:
        """ Инициализация объекта CurrencyConverterBot.
        :param token: Токен бота для авторизации. """
        self.bot = telebot.TeleBot(token)

        @self.bot.message_handler(commands=['start'])
        def handle_start(message: telebot.types.Message) -> None:
            """Обработчик команды /start. Отправляет приветственное сообщение.
               :param message: Объект сообщения от пользователя."""
            text = "Привет! Я бот для конвертации валют. \nПример: доллар рубль 100 \
                    \nИспользуйте команды /help или /values для получения информации."
            self.bot.send_message(message.chat.id, text)

        @self.bot.message_handler(commands=['help'])
        def handle_help(message: telebot.types.Message) -> None:
            """Обработчик команды /help. Отправляет список доступных команд.
               :param message: Объект сообщения от пользователя."""
            commands_list = [
                "/start - Начать",
                "/help - Показать список команд",
                "/values - Получить информацию о доступных валютах",
                "валюта1 валюта2 количество - Получить конвертацию"
                "\nПример: доллар рубль 100"
            ]
            self.bot.send_message(message.chat.id, '\n'.join(commands_list))

        @self.bot.message_handler(commands=['values'])
        def handle_values(message: telebot.types.Message) -> None:
            """Обработчик команды /values. Отправляет список доступных валют.
              :param message: Объект сообщения от пользователя."""
            available_currencies = list(CODES.keys())
            currencies_text = f'Доступные валюты: \n{'\n'.join(available_currencies)}'
            self.bot.send_message(message.chat.id, currencies_text)

        @self.bot.message_handler(func=lambda message: True)
        def handle_convert(message: telebot.types.Message) -> None:
            """Обработчик для конвертации валюты. Обрабатывает входные данные, вызывает метод get_price,
               отправляет результат пользователю.
               :param message: Объект сообщения от пользователя."""
            try:
                command = message.text.lower().split()  # обработка запроса не зависимо от регистра с разделением
                if len(command) != 3:  # проверка на корректность формата запроса по количеству
                    raise APIException("\nУточните формат: валюта1 валюта2 количество \
                                       \nПример: доллар рубль 100")  # вывод исключения

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
                    raise APIException("Нельзя сконвертировать одну валюту")

                result = self.get_price(base_currency, quote_currency, amount)  # вызов метода запроса на ресурс
                result_message = f"Стоимость {amount} {base_currency} составляет: {round(result, 2)} {quote_currency}"
                # вывод результатов запроса в читаемом формате
                self.bot.send_message(message.chat.id, result_message)  # отправка сообщения пользователю
            except APIException as e:  # вызов исключения с ошибкой пользователя
                self.bot.send_message(message.chat.id, f"Ошибка ввода: {str(e)}")
            except Exception as e:  # вызов исключения с технической ошибкой от сервиса
                self.bot.send_message(message.chat.id, f"Технический сбой: {str(e)}")

    @staticmethod
    def get_price(base: str, quote: str, amount: float) -> float:
        """Получение стоимости конвертации валюты.
           :param base: Базовая валюта.
           :param quote: Валюта, в которую конвертируется.
           :param amount: Количество единиц базовой валюты.
           :return: Результат конвертации."""
        url = f'https://v6.exchangerate-api.com/v6/{api_key}/pair/{base}/{quote}'  # адрес API ресурса
        r = requests.get(url)  # создание GET запроса через библиотеку
        data = r.json()  # обработка ответа в формат JSON

        if data['result'] == 'error':  # проверка ответа от сервиса на внутренние ошибки (согласно сайта)
            error_type = data.get('error-type', 'unknown')
            error_message = f"API Error: {error_type}"
            error_messages = {
                'unsupported-code': 'Unsupported currency code',
                'malformed-request': 'Malformed request',
                'invalid-key': 'Invalid API key',
                'inactive-account': 'Inactive account (email not confirmed)',
                'quota-reached': 'Quota reached (maximum number of requests exceeded)'
            }
            error_message += f" - {error_messages.get(error_type, 'unknown')}"
            raise APIException(error_message)

        if 'conversion_rate' not in data:  # проверка наличия требуемых данных в ответе от ресурса
            raise APIException(f"Invalid or unsupported quote currency: {quote}")

        try:  # проверка на наличие результат с требуемым курсом запрашиваемых валют
            rate = data['conversion_rate']
        except KeyError:
            raise APIException(f"Failed to get conversion rate from the response")

        result = amount * rate  # определение стоимости валюты от курса
        return result  # возврат результата

    def run(self) -> None:
        """Запуск бота в режиме ожидания сообщений от пользователей."""
        self.bot.polling(none_stop=True)


if __name__ == '__main__':
    bot_main = CurrencyConverterBot(CURRENCY_TOKEN)  # создание объекта бот, установленного класса
    bot_main.run()  # запуск объекта в работу
