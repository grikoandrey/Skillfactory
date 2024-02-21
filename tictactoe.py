from colorama import Fore


def print_board(board):
    # Визуальный вывод игрового поля
    for row in board:
        # print(" | ".join(row))
        print(" | ".join([f"{color(cell)}" for cell in row]))
        print("-" * 9)


def check_winner(board):
    # Проверка строк
    for row in board:
        if all(cell == "X" for cell in row) or all(cell == "O" for cell in row):
            return True

    # Проверка столбцов
    for col in range(3):
        if all(board[row][col] == "X" for row in range(3)) or all(board[row][col] == "O" for row in range(3)):
            return True

    # Проверка диагоналей
    if all(board[i][i] == "X" for i in range(3)) or all(board[i][2 - i] == "O" for i in range(3)):
        return True
    if all(board[i][i] == "O" for i in range(3)) or all(board[i][2 - i] == "X" for i in range(3)):
        return True
    return False


def full_board(board):
    # return all(cell != " " for row in board for cell in row)
    return all(cell not in map(str, range(1, 10)) for row in board for cell in row)


def get_user_input(current_player):
    position = input(f'Игрок {current_player}, выберите позицию от 1 до 9: ')
    if position.isdigit() and 1 <= int(position) <= 9:
        return int(position) - 1  # уменьшаем на 1, чтобы получить индекс в матрице
    else:
        print('Некорректный ввод. Пожалуйста, введите число от 1 до 9.')
    return get_user_input(current_player)  # Рекурсивный вызов функции


def color(cell):
    if cell.isdigit():
        return f"{Fore.LIGHTBLACK_EX}{cell}{Fore.RESET}"  # Серый цвет для цифр
    elif cell == "X":
        return f"{Fore.RED}X{Fore.RESET}"  # Красный цвет для X
    elif cell == "O":
        return f"{Fore.BLUE}O{Fore.RESET}"  # Синий цвет для O


def tic_tac_toe():
    # Инициализация игры
    # board = [[" " for _ in range(3)] for _ in range(3)]
    board = [[str(i + j * 3 + 1) for i in range(3)] for j in range(3)]  # Создаем заполнение поля цифрами
    current_player = "X"  # создаем игрока с первым ходом

    while True:  # Запускаем игровой цикл
        print_board(board)  # Выводим исходное поле
        # row = int(input(f"Player {current_player}, enter row (1-3): ")) - 1
        # col = int(input(f"Player {current_player}, enter column (1-3): ")) - 1
        position = get_user_input(current_player)  # Принимаем от игрока номер ячейки
        row = position // 3  # находим позицию в строке
        col = position % 3  # находим позицию в столбце

        # if board[row][col] == "X" or "O":
        if board[row][col] == str(position + 1):  # выполняется проверка заполнености ячейки
            board[row][col] = current_player  # если ячейка свободна, записываем туда текущего игрока
            if check_winner(board):  # выполняем проверку победы по внешней функции
                print_board(board)  # выводим текущее поле
                print(f"Игрок {current_player} победил!")  # сообщаем о победе
                break  # выход из цикла
            elif full_board(board):  # выполняется проверка заполненности поля
                print_board(board)  # выводится текущее положение
                print("Ничья!")  # вывоводится сообщение о ничьей
                break  # выход из цикла
            else:
                current_player = "O" if current_player == "X" else "X"  # условия не соблюдаются, переход хода
        else:
            print("Ячейка занята, попробуйте снова.")  # вывод сообщения о заполнености ячейки


tic_tac_toe()
