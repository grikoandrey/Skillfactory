import time

from telebot import types

from tree2 import (load_quiz_data, result_message_text, logo_end_photo,
                   logo_start_quiz_photo, choice, choose_animal)


class Quiz:  # класс Викторина
    def __init__(self, bot):  # Инициализация класса Quiz с параметрами bot и questions
        # self.choice = choice
        # self.totem_animal_data = None
        self.result_tuples = None
        self.user_responses = []
        self.bot = bot  # Присвоение атрибуту bot ссылки на объект бота
        self.questions = self.load_quiz_data()  # Присвоение атрибуту questions списка вопросов
        self.current_question_index = 0  # Инициализация индекса текущего вопроса
        self.answers = []  # Инициализация списка ответов
        self.message_id = None
        self.current_question_text = None

    def start_quiz(self, chat_id):  # Метод для начала викторины с передачей идентификатора чата
        self.current_question_index = 0  # Сброс индекса текущего вопроса
        self.answers = []  # Очистка списка ответов
        # quiz_start_message = quiz_start_message_text
        logo_start_quiz = logo_start_quiz_photo
        with open(logo_start_quiz, "rb") as photo:
            # self.bot.send_photo(chat_id, photo, caption=quiz_start_message, parse_mode='HTML')
            self.bot.send_photo(chat_id, photo)
            time.sleep(3)
        # print(f"Значение self.totem_animal_data после сброса: {self.totem_animal_data}")
        self.send_question(chat_id)  # Вызов метода отправки первого вопроса

    @staticmethod
    def load_quiz_data():  # вызываем загрузку данных
        file_name = 'Questions'
        return load_quiz_data(file_name)  # Используем функцию из tree.py

    def send_question(self, chat_id):  # Метод для отправки вопроса с передачей идентификатора чата
        if self.current_question_index < len(self.questions):  # Проверка наличия вопросов для отправки
            image_number = self.current_question_index + 1  # Номер изображения соответствует индексу вопроса плюс 1
            image_path = f'MoscowZoo/Eng/logo_quiz_{image_number}.jpg'  # Путь к изображению
            with open(image_path, 'rb') as image_file:
                self.bot.send_photo(chat_id, image_file)
                time.sleep(6)
            question_data = self.questions[self.current_question_index]  # Получение данных текущего вопроса
            self.current_question_text = question_data['question']  # Получение текста вопроса
            markup = self.create_answer_markup(question_data["answers"])  # Создание разметки с вариантами ответов
            message = self.bot.send_message(chat_id, self.current_question_text,
                                            reply_markup=markup, parse_mode='Markdown')
            # Отправка сообщения с вопросом и разметкой
            self.message_id = message.message_id
        else:
            self.end_quiz(chat_id)  # если вопросов больше нет, заканчиваем викторину

    @staticmethod
    def create_answer_markup(answers):  # Метод для создания разметки с вариантами ответов
        markup = types.InlineKeyboardMarkup(row_width=1)  # Создание объекта разметки
        for i, answer in enumerate(answers, start=1):
            button_text = answer["text"]
            button_data = f"answer_{i}"
            button = types.InlineKeyboardButton(button_text, callback_data=button_data)
            markup.add(button)  # Добавление кнопки в разметку
        return markup  # Возврат сформированной разметки

    def process_answer(self, chat_id, answer_num):  # Метод для обработки ответа на вопрос
        rank = self.questions[self.current_question_index - 1]["answers"][answer_num - 1]["rank"]
        self.answers.append(rank)  # Добавление ранга ответа в список ответов
        # self.answers.append(answer_num)  # Добавление ответа в список ответов
        self.current_question_index += 1  # Увеличение индекса текущего вопроса
        print(f'На вопрос {self.current_question_index} выбран ответ с рангом: {rank}')
        # Получаем текст выбранного ответа из списка вариантов
        # Получаем ранг выбранного ответа из списка вариантов
        selected_answer = self.questions[self.current_question_index - 1]["answers"][answer_num - 1]["text"]
        response_message = f"{self.current_question_text}\nВаш ответ: {selected_answer}"
        self.user_responses.append(response_message)  # создание списка вопросов и ответов для отправки
        print(self.user_responses)
        self.bot.send_message(chat_id, response_message, parse_mode='Markdown')
        if self.message_id:
            self.bot.delete_message(chat_id, self.message_id)
        self.send_question(chat_id)

    def calculate_results(self):  # подсчет результатов как среднее между двумя аналогичными вопросам
        # Получаем ранги для первых и последних пяти ответов
        print(self.answers)
        first_ranks = self.answers[:5]
        last_ranks = self.answers[5:]
        self.result_tuples = [round(((first_ranks[i] + last_ranks[i]) / 2), 1) for i in range(5)]
        print(self.result_tuples)
        chosen_animal = choose_animal(self.result_tuples, choice)
        # print(chosen_animal)
        return chosen_animal

    def collection_of_information(self, user_id, full_name):  # сбор результатов для отправки сотруднику
        # results = self.calculate_results()
        # user_responses = self.user_responses
        user_info = {'user_id': user_id,
                     'full_name': full_name,
                     'user_responses': self.user_responses,
                     'results': self.result_tuples,
                     }
        return user_info

    def end_quiz(self, chat_id):  # завершение викторины
        # total_score = sum(self.answers)  # Подсчет суммы ответов пользователя
        # print('Итог викторины: ', total_score)
        result_message = result_message_text
        logo_end = logo_end_photo
        # Отправляем сообщение с фотографией логотипа зоопарка
        with open(logo_end, "rb") as photo:
            self.bot.send_photo(chat_id, photo, caption=result_message,
                                reply_markup=self.create_result_keyboard(), parse_mode='HTML')

    @staticmethod
    def create_result_keyboard():  # Создаем клавиатуру с двумя кнопками
        keyboard = types.InlineKeyboardMarkup()
        result_button = types.InlineKeyboardButton("Узнать результат", callback_data="show_result")
        restart_button = types.InlineKeyboardButton("Пройти снова", callback_data='restart_quiz')
        keyboard.add(result_button, restart_button)
        return keyboard
