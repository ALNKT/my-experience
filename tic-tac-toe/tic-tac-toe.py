from classes import Player, Board
from functions import *
import random


def start_game():
    """
    Начало игры.
    Вводится имя игрока, символ для игры.
    Выбирается оппонент (компьютер или второй игрок).
    Предлагается ознакомиться с правилами игры. После чего начинается игра.
    После окончания игры можно сыграть еще раз.
    """
    one_more = 'да'

    while one_more == 'да':
        print('Добро пожаловать в игру крестики-нолики!')
        board = Board()
        player = Player(input('Введите ваше имя: '))
        player.symbol = input('Введите символ для игры ("x" или "0"): ')

        while player.symbol not in 'xх0o':
            player.symbol = input('Введите корректный символ для игры ("x" или "0"): ')

        opponent = int(input(f'{player.name}, выберите оппонента: компьютер (1), второй игрок (2): '))
        if opponent == 1:
            comp = Player('Компьютер')
        if opponent == 2:
            comp = Player(input('Введите ваше имя: '))

        if player.symbol in 'xх':
            comp.symbol = '0'
        else:
            comp.symbol = 'x'

        print(f'\nРады Вас приветствовать Вас, {player.name} и {comp.name}! Давайте начнём!')
        rules = int(input('Чтобы прочитать правила, введите 1, если Вы знаете правила, введите 0: '))

        if rules:
            print_rules(board)

        lst_pos = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        while len(lst_pos) > 0:
            player.position = int(input(f'{player.name}, введите номер клетки: '))
            while player.position not in lst_pos:
                player.position = int(input(f'{player.name}, некорректный ввод. Введите позицию: '))
            lst_pos.remove(player.position)
            board.create_cell(player.position, player.symbol)
            if opponent == 2:
                print_board(board)
            if check_winner(board.field, player.symbol):
                print(f'\n{"У нас есть победитель!".center(70)}\n{player.name}. Поздравляем!!!')
                print_board(board)
                break
            if opponent == 1:
                if len(lst_pos) != 0:
                    print('Ход компьютера')
                    while comp.position not in lst_pos:
                        comp.position = random.choice(lst_pos)
                    lst_pos.remove(comp.position)
            else:
                if len(lst_pos) != 0:
                    comp.position = int(input(f'{comp.name}, введите номер клетки: '))
                    while comp.position not in lst_pos:
                        comp.position = int(input(f'{comp.name}, некорректный ввод. Введите позицию: '))
                    lst_pos.remove(comp.position)
            board.create_cell(comp.position, comp.symbol)
            if check_winner(board.field, comp.symbol):
                print(
                    f'\n{"У нас есть победитель!".center(70)}\nЭто {comp.name}!\n{player.name}, не расстраивайтесь, '
                    f'повезет в другой раз!')
                print_board(board)
                break
            print_board(board)
        else:
            print('Ничья!')
        one_more = input('\nСыграем еще раз? ')


start_game()
