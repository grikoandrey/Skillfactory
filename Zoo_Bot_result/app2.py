import telebot  # Импортируем библиотеку telebot
from telebot import types  # Импортируем типы сообщений из библиотеки telebot
import time
from decouple import config

from quiz2 import Quiz  # Импортируем класс Quiz из модуля quiz1

from tree2 import greetings_generator1, greetings_generator2, start_generator, \
    get_totem_animal_data, default_response_text, help_message_text, \
    logo_greeting_photo, info_message_text, info_guardian_url, \
    guardian_message_text, send_message_text, contacts_message_text, send_email_to_zoo, share_result_text, serious_text
# Импортируем генераторы приветствий из модуля tree


class LogoFileNotFoundException(Exception):  # Определяем пользовательское исключение наследующееся от базового класса
    pass


class BotManager:  # Определяем класс BotManager
    def __init__(self, token):  # Определяем конструктор класса с аргументом token
        self.bot = telebot.TeleBot(token)  # Создаем экземпляр класса TeleBot и присваиваем его атрибуту bot
        self.quiz = Quiz(self.bot)  # Создаем экземпляр класса Quiz, передавая ему объект бота
        self.setup_handlers()  # Вызываем метод setup_handlers для настройки обработчиков
        self.totem_animal_data = None
        self.result_animal = None

    def start_bot(self):  # Определяем метод start_bot
        self.bot.polling(none_stop=True)  # Запускаем бота

    def setup_handlers(self):  # Определяем метод для настройки обработчиков
        self.setup_message_handler()  # Вызываем метод
        self.setup_callback_handler()  # Вызываем метод

    def setup_message_handler(self):  # Определяем метод для настройки обработчика сообщений
        @self.bot.message_handler(func=lambda message: message.text.startswith('Отзыв'))
        def handle_feedback_message(message):
            try:
                if self.totem_animal_data is not None:
                    user_id = str(message.from_user.id)
                    full_name = f"{message.from_user.first_name} {message.from_user.last_name}"
                    subject = f'Отзыв от пользователя: {full_name}, ID: {user_id}'
                    results = message.text
                    print(results)
                    if send_email_to_zoo(results, subject):
                        send_message = 'Спасибо за ваш отзыв! Он был получен и передан на обработку.'
                        self.bot.reply_to(message, send_message)
                        # time.sleep(5)
                        # user_name = message.from_user.first_name
                        # self.send_greeting_with_buttons(user_name)
                    else:
                        send_message = 'Не удалось обработать запрос, попробуйте позже'
                        self.bot.reply_to(message, send_message)
            except TypeError:
                send_message = 'Викторина еще не пройдена, возможно у Вас еще не сложилось мнение.'
                answer = self.bot.send_message(message.chat.id, send_message)
                time.sleep(2)
                self.bot.delete_message(message.chat.id, message.message_id)
                time.sleep(4)
                self.bot.delete_message(message.chat.id, answer.message_id)

        @self.bot.message_handler(func=lambda message: True)  # Создаем обработчик сообщений
        def handle_messages(message):  # Определяем функцию-обработчик сообщений
            command_handlers = {  # Создаем словарь с обработчиками команд
                'привет': self.send_greeting_with_buttons,  # При получении команды вызываем метод
                '/start': self.send_start_menu_keyboard,
                '/help': self.send_help_message,
                '/info': self.send_info_message,
                '/contacts': self.send_contacts,
                'подтверждаю': self.agreement,
                # '/clear': self.clear_chat,
            }
            command = message.text.lower()  # Приводим текст сообщения к нижнему регистру
            handler = command_handlers.get(command, self.send_default_response)  # Получаем обработчик для
            # команды или send_default_response, если команда не найдена
            handler(message)  # Вызываем обработчик с переданным сообщением

    def setup_callback_handler(self):  # Определяем метод для настройки обработчика обратных вызовов
        @self.bot.callback_query_handler(func=lambda call: True)  # Создаем обработчик обратных вызовов
        def callback_handler(call):  # Определяем функцию-обработчик обратных вызовов
            # print('Кнопка нажата!')
            command_handlers = {  # Создаем словарь с обработчиками команд
                'learn_more': self.send_info_message,  # При получении команды вызываем метод
                'become_guardian?': self.send_become_guardian_info,
                'start_quiz': self.send_start_quiz_message,
                'start': self.send_start_menu_keyboard,
                'help': self.send_help_message,
                'info': self.send_info_message,
                'contacts': self.send_contacts,
                'continue': self.processing_of_results,
                # **{f'answer_{i}': lambda message, idx=i: self.quiz.process_answer(message.chat.id, i) for i in
                #    range(1, 5)},
                # 'process_answer': self.quiz.process_answer,
                'restart_quiz': self.send_start_quiz_message,
                'show_result': self.show_totem_animal_info,
                'presentation': self.load_presentation,
                'get_res': self.load_result_list,
                'become_a_guardian': self.become_a_guardian,
                # 'agreement': self.agreement,
                'some_serious': self.some_serious,

            }
            # Добавляем обработчик для каждого вопроса
            for i in range(1, 5):
                command_handlers[f'answer_{i}'] = lambda message, idx=i: self.quiz.process_answer(message.chat.id, idx)
            command = call.data  # Сохраняем данные обратного вызова в переменную command
            handler = command_handlers.get(command)  # Получаем обработчик для команды
            if handler:  # Если обработчик найден
                handler(call.message)  # Вызываем обработчик с сообщением обратного вызова

    def send_greeting_with_buttons(self, message):  # Определяем метод для отправки приветственного сообщения
        markup = types.InlineKeyboardMarkup(row_width=2)  # Создаем разметку для кнопок
        button_start = types.InlineKeyboardButton("СТАРТ", callback_data='start')  # Создаем кнопку 'СТАРТ'
        button_help = types.InlineKeyboardButton("Помощь", callback_data='help')  # Создаем кнопку 'Помощь'
        button_info = types.InlineKeyboardButton("Информация", callback_data='info')  # Создаем кнопку 'Информация'
        markup.add(button_start)  # Добавляем кнопку 'СТАРТ' в разметку
        markup.add(button_help, button_info)  # Добавляем кнопки 'Помощь' и 'Информация' в разметку
        user_name = message.from_user.first_name  # Получаем имя пользователя
        greet1 = greetings_generator1.get_random_text()  # Генерируем случайное приветствие
        greet2 = greetings_generator2.get_random_text()  # Генерируем случайное приветствие
        greeting = f"{greet1}, {user_name}! {greet2}"  # Формируем приветственное сообщение
        self.bot.send_message(message.chat.id, greeting, reply_markup=markup)  # Отправляем приветственное сообщение

    def send_start_menu_keyboard(self, message):  # Определяем метод для отправки меню старта
        greet2 = greetings_generator2.get_random_text()  # Генерируем случайное приветствие
        greeting = f"{greet2}"  # Формируем приветственное сообщение
        markup = types.InlineKeyboardMarkup()  # Создаем разметку для кнопок
        button_learn_more = types.InlineKeyboardButton("Узнать больше", callback_data='learn_more')
        button_become_guardian = types.InlineKeyboardButton("Стать опекуном?", callback_data='become_guardian?')
        button_start_quiz = types.InlineKeyboardButton("ВИКТОРИНА", callback_data='start_quiz')
        markup.add(button_start_quiz)  # Добавляем кнопку 'ВИКТОРИНА' в разметку
        markup.add(button_become_guardian, button_learn_more)  # Добавляем кнопки в разметку
        try:  # Обрабатываем исключения
            self.bot.send_message(message.chat.id, greeting)
            logo_greeting = logo_greeting_photo  # Изображение логотипа
            with open(logo_greeting, 'rb') as logo:  # Открываем файл с логотипом
                start_greet = start_generator.get_random_text()  # Генерируем случайное приветствие
                start_menu_message = f"{start_greet}:"  # Формируем сообщение меню старта
                self.bot.send_photo(message.chat.id, logo, caption=start_menu_message, reply_markup=markup)
                # Отправляем сообщение с логотипом и кнопками
        except FileNotFoundError:  # Обрабатываем исключение FileNotFoundError
            raise LogoFileNotFoundException("Файл логотипа не найден.")  # Вызываем исключение

    def send_help_message(self, message):  # метод для отправки сообщения со справкой
        help_message = help_message_text
        self.bot.send_message(message.chat.id, help_message)  # Отправляем сообщение со справкой

    def send_contacts(self, message):  # отправка контактов зоопарка
        contacts_message = contacts_message_text
        self.bot.send_message(message.chat.id, contacts_message)

    def send_info_message(self, message):  # Определяем метод для отправки информационного сообщения
        info_url = "https://moscowzoo.ru/"  # URL для получения дополнительной информации
        markup = types.InlineKeyboardMarkup()  # Создаем разметку для кнопки
        info_button = types.InlineKeyboardButton("Посетить сайт зоопарка", url=info_url)  # Создаем кнопку для
        # посещения сайта зоопарка
        markup.add(info_button)  # Добавляем кнопку в разметку
        info_message = info_message_text  # Формируем информационное сообщение
        self.bot.send_message(message.chat.id, info_message, reply_markup=markup)  # Отправляем сообщение

    def send_become_guardian_info(self, message):  # метод для становлении опекуном
        guardian_message = guardian_message_text  # Формируем сообщение о становлении опекуном
        info_guardian = info_guardian_url
        keyboard = types.InlineKeyboardMarkup()
        button_info_guardian = types.InlineKeyboardButton('Ознакомиться с программой', url=info_guardian)
        button_presentation_get = types.InlineKeyboardButton("Получить презентацию", callback_data='presentation')
        button_get_contacts = types.InlineKeyboardButton('Контакты', callback_data='contacts')
        keyboard.add(button_info_guardian)
        keyboard.add(button_presentation_get)
        keyboard.add(button_get_contacts)
        self.bot.send_message(message.chat.id, guardian_message, reply_markup=keyboard)  # Отправляем сообщение

    def load_presentation(self, message):  # метод загрузки презентации пользователю
        self.bot.send_document(message.chat.id, document=open('presentation.pdf', 'rb'), caption='презентация')

    def send_start_quiz_message(self, message):  # метод для начала викторины
        self.quiz.start_quiz(message.chat.id)  # Вызываем метод start_quiz из класса Quiz
        self.totem_animal_data = None  # обнуляем результат викторины

    def send_default_response(self, message):  # метод для обработки любого сообщения и его удаления
        default_response = default_response_text  # Формируем ответ
        answer = self.bot.send_message(message.chat.id, default_response)  # Отправляем ответ
        time.sleep(3)
        self.bot.delete_message(message.chat.id, message.message_id)
        time.sleep(6)
        self.bot.delete_message(message.chat.id, answer.message_id)

    def show_totem_animal_info(self, message):  # метод для обощения результатов и вывода пользователю
        try:
            if not self.totem_animal_data:
                self.result_animal = self.quiz.calculate_results()
                print("Определено животное:", self.result_animal)  # Выводим обновленное значение
                self.totem_animal_data = get_totem_animal_data(self.result_animal)
                # self.update_totem_animal_data(result_animal)  # Обновляем данные о результате викторины
            animal_data = self.totem_animal_data
            print("Получен список по животному:", animal_data)  # Выводим текущее значение
            photo_url = animal_data.get('image_url', '')
            # Формируем текст сообщения с информацией о тотемном животном
            text = f"<b>{animal_data['name']}</b>\n"
            text += f"{animal_data['description']}\n"
            msg = '<b>Результаты получены! Вперед!</b>'
            markup = types.InlineKeyboardMarkup()
            button_continue = types.InlineKeyboardButton('Приключения продолжаются...', callback_data='continue')
            markup.add(button_continue)
            if photo_url:
                photo = open(photo_url, 'rb')
                self.bot.send_photo(message.chat.id, photo, caption=text, parse_mode='HTML')
                time.sleep(3)
                answer = self.bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode='HTML')
                # time.sleep(4)
                # self.bot.delete_message(message.chat.id, answer.message_id)
            # Отправляем фотографию тотемного животного
        except Exception as e:
            error_message = "Пройдите викторину для получения результата."
            answer = self.bot.send_message(message.chat.id, error_message)
            print(f"Ошибка: {e}. Список результатов пуст.")
            time.sleep(3)
            self.bot.delete_message(message.chat.id, answer.message_id)

    def processing_of_results(self, message):  # обработка результатов викторины и представление итогов
        if not self.totem_animal_data:
            # self.result_animal = self.quiz.calculate_results()
            self.totem_animal_data = get_totem_animal_data(self.result_animal)
            # self.result_animal = result_animal  # Сохраняем результат в атрибуте объекта
        animal_data = self.totem_animal_data
        website_url = animal_data.get('website_url', '')
        text = '<b>Вы прошли немалый путь, остался один шаг! Но выбор труден..</b>'
        keyboard = types.InlineKeyboardMarkup()
        button_info = types.InlineKeyboardButton("Узнать больше о животном", url=website_url)
        button_get_result = types.InlineKeyboardButton('Скачать результат', callback_data='get_res')
        button_get_res_mail = types.InlineKeyboardButton('Немного о серьезном..', callback_data='some_serious')
        button_info_guardian = types.InlineKeyboardButton('Стать опекуном?', callback_data='become_guardian?')
        button_become_guardian = types.InlineKeyboardButton('Стать опекуном!', callback_data='become_a_guardian')
        button_quiz_repeat = types.InlineKeyboardButton("Попробовать снова?", callback_data='start')
        keyboard.row(button_info)
        keyboard.row(button_get_result)
        keyboard.row(button_get_res_mail)
        keyboard.row(button_info_guardian)
        keyboard.row(button_become_guardian)
        keyboard.row(button_quiz_repeat)
        self.bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='HTML')

    def load_result_list(self, message):  # загрузка итога, чтобы поделиться с друзьями
        # result_animal = getattr(self, 'result_animal', None)  # Получаем результат из атрибута объекта
        if self.result_animal is not None:
            self.bot.send_document(message.chat.id,
                                   document=open(f'./for_Bot/res_list_animals/{self.result_animal}.jpg', 'rb'),
                                   caption='тотемное животное')
            time.sleep(2)
            share_result_message = share_result_text
            self.bot.send_message(message.chat.id, share_result_message)
        else:
            # Если результат не найден, отправляем сообщение об ошибке
            answer = self.bot.send_message(message.chat.id, "Результат не найден.")
            time.sleep(3)
            self.bot.delete_message(message.chat.id, answer.message_id)

    def become_a_guardian(self, message):  # вывод сообщения о подтверждении стать опекуном
        send_message = send_message_text
        # keyboard = types.InlineKeyboardMarkup()
        # button_agreement = types.InlineKeyboardButton('Подтвердить', callback_data='agreement')
        # keyboard.row(button_agreement)
        self.bot.send_message(message.chat.id, send_message, parse_mode='HTML')

    def some_serious(self, message):  # сообщение о серьзном
        send_message = serious_text
        self.bot.send_message(message.chat.id, send_message, parse_mode='HTML')

    def agreement(self, message):  # метод сбора результатов и отправки на почту сотрудников
        try:
            user_id = message.from_user.id
            full_name = f"{message.from_user.first_name} {message.from_user.last_name}"
            user_info = self.quiz.collection_of_information(user_id, full_name)
            subject = 'Результаты викторины от Зоо-бота'
            animal_data = self.totem_animal_data
            results = str({**user_info, **animal_data})
            print(results)
            if send_email_to_zoo(results, subject):
                send_message = 'Отправлено'
            else:
                send_message = 'Не удалось отправить, попробуйте позже'
            self.bot.send_message(message.chat.id, send_message)
        except TypeError:
            send_message = 'Викторина еще не пройдена, ввод данного слова необходим позже'
            answer = self.bot.send_message(message.chat.id, send_message)
            time.sleep(2)
            self.bot.delete_message(message.chat.id, message.message_id)
            time.sleep(4)
            self.bot.delete_message(message.chat.id, answer.message_id)

    # def clear_chat(self, message):  # Определяем метод clear_chat для удаления сообщения
    #     chat_id = message.chat.id  # Получаем идентификатор чата
    #     message_id = message.message_id  # Получаем идентификатор сообщения
    #     self.bot.delete_message(chat_id, message_id)  # Удаляем сообщение


# Создаем экземпляр класса и запускаем бота
if __name__ == '__main__':
    bot_key = config('AYGO_ZOO_BOT')
    bot_manager = BotManager(bot_key)  # Создаем экземпляр класса BotManager,
    # передавая ему токен бота
    bot_manager.start_bot()  # Запускаем бота
