class Cell:
    """
    Класс клетка поля

    Args:
        number (int): номер клетки
        value (str): значение клетки (символ "х" или "0")
    """

    def __init__(self, number, value=' '):
        self.number = number
        self.value = value

    def check_cell(self):
        """
        Проверка клетки поля на отсутствие символа в ней

        :return: True, если клетка занята, иначе False
        :rtype: bool
        """
        if self.value == ' ':
            return False
        return True


class Board:
    """
    Класс Доска (Поле). Создает экземпляры клеток поля

    Args:
        field (list): доска (поле) с клетками
    """

    def __init__(self):
        self.field = [[Cell(j + i) for i in range(1, 4)] for j in range(0, 9, 3)]

    def create_cell(self, position: int, value: str) -> None:
        """
        Создает экземпляр клетки поля

        :param position: позиция клетки поля
        :type position: int
        :param value: значение клетки поля
        :type value: str
        """
        for i_position in self.field:
            for i_number in i_position:
                num = i_number.number
                if position == num:
                    if not i_number.check_cell():
                        i_number.value = value


class Player:
    """
    Класс игрок

    Args:
        name (str): имя игрока
        position (int): позиция игрока (клетка поля, в которую игрок ставит символ "х" или "0").
        symbol (str): символ, которым играет игрок
    """

    def __init__(self, name, position='', symbol=''):
        self.name = name
        self.position = position
        self.symbol = symbol
