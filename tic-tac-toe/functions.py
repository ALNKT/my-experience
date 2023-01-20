def print_board(board):
    """
    Выводит текущее состояние игрового поля

    :param board: поле с клетками
    :type board: class
    """
    for index, i_ceil in enumerate(board.field):
        print(' {} | {} | {} '.format(*[i_number.value for i_number in i_ceil]))
        if index != 2:
            print('---|---|---')


def check_winner(current_board, sym):
    """
    Проверка наличия победителя в игре

    :param current_board: текущее состояние игрового поля
    :type current_board: class
    :param sym: символ игрока
    :type sym: str
    :return: True, если есть победитель, False иначе
    :rtype: bool
    """
    for i_lst_cells in current_board:
        if len([i_cell.value for i_cell in i_lst_cells if
                i_cell.value == sym]) == 3:  # Проверяем одинаковые символы в строках матрицы
            return True
    if len([i_lst_cell[0].value for i_lst_cell in current_board if
            i_lst_cell[0].value == sym]) == 3:  # Проверяем одинаковые символы в 1-м столбце матрицы
        return True
    elif len([i_lst_cell[1].value for i_lst_cell in current_board if
              i_lst_cell[1].value == sym]) == 3:  # Проверяем одинаковые символы во 2-м столбце матрицы
        return True
    elif len([i_lst_cell[2].value for i_lst_cell in current_board if
              i_lst_cell[2].value == sym]) == 3:  # Проверяем одинаковые символы в 3-м столбце матрицы
        return True
    elif len([current_board[i][i].value for i in range(3)
              if current_board[i][i].value == sym]) == 3:  # Проверяем одинаковые символы по главной диагонали матрицы
        return True
    elif len([current_board[2 - i][i].value for i in range(2, -1, -1) if
              current_board[2 - i][i].value == sym]) == 3:  # Проверяем одинаковые символы по побочной диагонали матрицы
        return True
    return False


def print_rules(board):
    """
    Вывод справки по правилам игры

    :param board: игровое поле
    :type board: class
    """
    print('''\n{}
Поле имеет размер 3х3. Каждая клетка поля пронумерована от 1 до 9 (включительно).
Для того, чтобы установить свое значение в клетку, Вам необходимо указать номер этой клетки в поле для ввода.
Поле пронумеровано следующим образом:'''.format('Правила игры:'.center(80)))
    for index, i_ceil in enumerate(board.field):
        print(' {} | {} | {} '.format(*[i_number.number for i_number in i_ceil]))
        if index != 2:
            print('---|---|---')
