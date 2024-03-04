import random
import os
import smtplib

from decouple import config
# from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# параметры базовых тотемных животных
choice = {(1.5, 1, 2, 3, 3): 'змея', (2, 3, 3, 3, 3): 'крокодил', (2.5, 2, 1, 1, 1): 'черепаха',
          (3, 1, 1, 1, 2): 'бабочка', (3, 2, 3, 2, 2): 'орел', (2, 2, 1, 1, 1): 'утка',
          (3, 2, 1, 1, 2): 'попугай', (3, 2, 2, 2, 3): 'сова', (1, 2, 1, 2, 2): 'обезьяна',
          (1, 3, 1, 2, 3): 'жираф', (1, 1, 2, 1, 1): 'еж', (1, 2, 3, 3, 2): 'волк',
          (1, 3, 3, 3, 3): 'барс', (1, 1, 3, 2, 1): 'лиса',
          }


def send_email_to_zoo(results, subject):  # функция отправки итогов на почту сотрудника
    sender = config('GMAIL_USER')
    password = config('GMAIL_KEY_PYTHON')
    recipient = 'MAILRU_USER'

    msg = MIMEText(results)  # создаем объект сообщения
    msg['Subject'] = subject  # 'Результаты викторины от Зоо-бота'
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Подключение к серверу SMTP
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
            print('Success!')
            return True
    except Exception as e:
        print(f'{e}\n Check login или password, please.')
        return False


# def send_email_to_yourself(results, e_mail):  # пока отключена
#     server = smtplib.SMTP('smtp.gmail.com', 587)  # Подключение к серверу SMTP
#     server.starttls()
#     server.login('griko.and@gmail.com', config('GMAIL_KEY_PYTHON'))
#
#     msg = MIMEMultipart()  # Создание сообщения
#     msg['From'] = 'your_email@example.com'
#     msg['To'] = e_mail
#     msg['Subject'] = 'Результаты викторины'
#
#     # Текст сообщения
#     body = '\n'.join([f'{question}: {answer}' for question, answer in results.items()])
#     msg.attach(MIMEText(body, 'plain'))
#
#     server.send_message(msg)
#     server.quit()


def load_quiz_data(quiz_data):  # загрузка данных для викторины (вопросов и ответов)
    file_path = os.path.join("for_Bot/zoo_info", f"{quiz_data.lower()}")
    if not os.path.isfile(file_path):
        return f"Файл {quiz_data} не обнаружен."
    questions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        question_data = {}
        is_question = False
        for line in file:
            line = line.strip()
            if line.startswith("question:"):  # Начало нового вопроса
                is_question = True
                if question_data:  # Добавляем предыдущий вопрос
                    questions.append(question_data)
                question_data = {"question": line.split(": ", 1)[1]}  # Получаем текст вопроса
            elif line.startswith("answers:"):  # Ответы к текущему вопросу
                is_question = False
                answers = []
                for ans in line.split(": ")[1].split("; "):
                    answer_number, ans_text_rank = ans.split(". ")  # Разделяем номер ответа и текст с рангом
                    ans_text, rank = ans_text_rank.split(":")  # Разделяем текст ответа и его ранг
                    # text, rank = ans.split(":")
                    answers.append({"number": int(answer_number),
                                    "text": ans_text.strip(), "rank": float(rank.strip())})  # Изменяем структуру
                question_data["answers"] = answers
            elif is_question:  # Если строка принадлежит вопросу
                question_data["question"] += "\n" + line
        if question_data:  # Добавляем последний вопрос
            questions.append(question_data)
    return questions


# Пример использования:
# quiz_name = "Questions"  # Здесь указывается имя файла без расширения
# Questions = load_quiz_data(quiz_name)
# print(Questions)
#
# for idx, question in enumerate(Questions, 1):
#     print(f'{question['question']}')
#     print("Ответы:")
#     for answer in question['answers']:
#         print(f"{answer['number']} - {answer['text']} (Ранг: {answer['rank']})")

def choose_animal(user_params, choices):  # функция для определения максимально близкого совпадения
    best_match = None
    min_difference = float('inf')  # Начальное значение для минимальной разницы (принимаем максимальное значение)

    for params, animal in choices.items():  # Проходимся по каждому варианту в списке животных
        difference = sum(abs(user_param - param) for user_param, param in zip(user_params, params))
        # Считаем сумму разниц между параметрами пользователя и параметрами текущего животного

        if difference < min_difference:  # Если текущая разница меньше минимальной
            min_difference = difference  # Обновляем минимальную разницу
            best_match = animal  # Обновляем лучшее соответствие

    return best_match  # Возвращаем лучшее соответствие


# user = [3, 3, 1, 1, 1]
# my_animal = choose_animal(user, choice)
# print(my_animal)


def get_totem_animal_data(anim_name):  # сбор информации о животном из текстовых файлов на основании результата
    file_path = os.path.join("for_Bot/totem_animals", f"{anim_name.lower()}")
    if not os.path.isfile(file_path):
        return f"Данные о тотемном животном {anim_name} не найдены."
    animal_info = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        # info_message = f"Информация о тотемном животном {anim_name}:\n"
        for line in file:
            key, value = line.strip().split(": ", 1)
            animal_info[key] = value
    return animal_info


# Пример использования:
# animal_name = "Орел"
# animal_info = get_totem_animal_data(animal_name)
# print(animal_info)


class RandomTextGenerator:  # класс для рандомной генерации приветствий из файлов
    def __init__(self, file_path):
        self.file_path = file_path
        self.text_list = self.read_text_from_file()

    def read_text_from_file(self):
        if not os.path.isfile(self.file_path):
            print(f"Внимание: Файл '{self.file_path}' не существует.")
            return []
        with open(self.file_path, 'r', encoding='utf-8') as file:
            text_list = file.readlines()
        return text_list

    def get_random_text(self):
        if not self.text_list:
            return f"Файл '{self.file_path}' пуст."

        random_text = random.choice(self.text_list)
        return random_text.strip()


greetings_generator1 = RandomTextGenerator('for_Bot/greet1_list')
greetings_generator2 = RandomTextGenerator('for_Bot/greet2_list')
start_generator = RandomTextGenerator('for_Bot/start_list')

# result = get_totem_animal_data('Орел')
# send_email_to_zoo(result)

# send_email_to_yourself(result, email)

'''Тексты и ссылки служебных и приветственных сообщений'''
# Фото на стартовое меню перед началом викторины
logo_greeting_photo = "MoscowZoo/start_logo.jpg"
# Ответ на любое некорректное сообщение от пользователя (send_default_response)
default_response_text = ('Извините, я не понимаю ваш запрос 🧐.\nДавайте начнем с приветствия!'
                         '\n️⬇️⬇️️ выберите команду из меню или отправьте ПРИВЕТ')
# Текст на команду /info Информация
info_message_text = ("Узнайте больше о зоопарке! Это бот Московского зоопарка. Данный бот разработан для ознакомления "
                     "с программой опекунства, созданной Московским зоопарком, с целью привлечь людей для поддержки "
                     "животных, путем проведения шуточной викторины по определению тотемного животного.")
# Текст на команду /help
help_message_text = ('Это дружелюбный и безобидный бот. Ниже расположен список команд, которые Вы можете выбрать, '
                     'нажав на них или ввести текстом в виде сообщения. Любые другие сообщения не буду распознаны, '
                     'поэтому, пожалуйста, соблюдайте корректность.\nКоманды:\n'
                     '/start - Начать викторину\n/help - Получить справку\n/info - Информация о зоопарке')
# Текст сообщения с контактами
contacts_message_text = ('Для дополнительной информации Вы можете связаться с сотрудниками зоопарка по следующим '
                         'реквизитам:\ne-mail: opeka@moscow.zoo\n телефон: +7(495) 111-11-11')
# Текст о программе опекунства на сайте и презентации
guardian_message_text = ("Для более полной, точной и актуальной информации о программе опекунства, Вы можете посетить "
                         "сайт или получить презентацию. Выбор за Вами, только нажмите нужную кнопку")
# Текст и картинка начала викторины
quiz_start_message_text = '<b>Внимание! Викторина начинается!</b>'
logo_start_quiz_photo = 'MoscowZoo/Eng/logo_quiz.jpg'
# Текст и картинка итога викторины
result_message_text = ("<b>Поздравляем, викторина завершена, а Вы большой молодец!</b>\n"
                       "На основании Ваших ответов, подготовлены результаты по прохождению викторины, "
                       "выбран 'символ' и если Вы готовы узнать, то жмите кнопку ниже .")
logo_end_photo = 'MoscowZoo/Circle/MZoo-logo-ßircle-mono-white-small-preview.jpg'
info_guardian_url = 'https://moscowzoo.ru/my-zoo/become-a-guardian/'
# Текст для заключительного сообщения при отправке данных пользователя специалисту
send_message_text = ('Вы успешно завершили Викторину и возможно, пусть не до конца приняли решение стать опекуном '
                     'животного. Вы герой! А мы достигли своей цели, Спасибо!'
                     '\nДля дальнейшего этапа, необходимо Ваше согласие на отправку результатов викоторины специалисту '
                     'Московского зоопарка.\nВам необходимо ввести слова - <b>"Подтверждаю".</b>\n'
                     'Далее Вы можете связаться со специалистами, чтобы подтвердить и зафиксировать опекунство по'
                     'следующим контактам:\ne-mail: opeka@moscow.zoo\n телефон: +7(495) 111-11-11')
# Текст для сообщения при отправке итогового результата пользователю
share_result_text = ('Теперь когда Вы получили результат Викторины, Вы можете поделиться им с друзьями, переслав'
                     ' данное сообщение.')
serious_text = ('Вы завершили викторину. Это здорово! На самом деле это довольно шуточный проект, но его суть '
                'составляет очень важное и нужное дело. Результат является собирательным образом на основании Ваших '
                'ответов и не важно какое это животное, важно Ваше внимание. '
                ' Но если, вдруг, у Вас действительно возникнет желание стать опекуном '
                'пусть не именно данного животного, сотрудники Московского зоопрака с удовольствием расскажут '
                'гораздо больше и помогут сделать выбор для добрых дел!\nЕсли у Вас остались '
                'вопросы или желание еще раз ответить на вопросы, то можете вернуться к предыдущему меню и выбрать.'
                '\n<b>Оставить отзыв</b>\nпри желании Вы можете оставить отзыв о работе данного бота, чтобы '
                'это сделать отправьте пожалуйста сообщение, которое начинается на слово <b>Отзыв</b> '
                '(с большой буквы) а дальше сам текст. Спасибо.')
