class House:
    """
    Класс Дом, в котором живут люди и домашние животные

    __total_dirt: общее количество убранной грязи

    Args:
        money (int): кол-во денег в тумбочке
        fridge (int): кол-во еды в холодильнике
        cat_food (int): кол-во еды для кота
        dirt (int): кол-во грязи в доме
        name (str): название дома
    """

    __total_dirt = 0

    def __init__(self, money=100, fridge=50, cat_food=30, dirt=0, name='Дом, любимый дом'):
        self.__money = money
        self.__fridge = fridge
        self.__cat_food = cat_food
        self.__dirt = dirt
        self.__name = name

    def __str__(self):
        return f'\nДом: {self.__name}    Денег: {self.__money}    Еды: {self.__fridge}    Корма для кота: ' \
               f'{self.__cat_food}    Уровень грязи: {self.__dirt}    Всего убрано грязи: {self.__total_dirt} кг.'

    def get_total_dirt(self):
        """
        Геттер для получения общего кол-ва убранной грязи
        @return: __total_dirt
        @rtype: int
        """
        return self.__total_dirt

    def get_money(self):
        """
        Геттер для получения денег в доме

        @return: __money
        @rtype: int
        """
        return self.__money

    def get_fridge(self):
        """
        Геттер для получения кол-ва еды в холодильнике

        @return: __fridge
        @rtype: int
        """
        return self.__fridge

    def get_cat_food(self):
        """
        Геттер для получения кол-ва еды у кота

        @return: __cat_food
        @rtype: int
        """
        return self.__cat_food

    def get_dirt(self):
        """
        Геттер для получения кол-ва грязи в доме

        @return: __dirt
        @rtype: int
        """
        return self.__dirt

    def get_name(self):
        """
        Геттер для получения названия дома

        @return: __name
        @rtype: str
        """
        return self.__name

    def set_total_dirt(self, amount_dirt):
        """
        Сеттер для изменения общего кол-ва убранной грязи

        @param amount_dirt: кол-во грязи
        @type amount_dirt: int
        """
        self.__total_dirt += amount_dirt

    def set_money(self, money):
        """
        Сеттер для изменения кол-ва денег в доме

        @param money: новое кол-во денег
        @type money: int
        """
        self.__money = money

    def set_fridge(self, fridge):
        """
        Сеттер для изменения кол-ва еды в холодильнике

        @param fridge: новое кол-во еды
        @type fridge: int
        """
        self.__fridge = fridge

    def set_cat_food(self, cat_food):
        """
        Сеттер для изменения кол-ва еды для кота в доме

        @param cat_food: новое кол-во еды
        @type cat_food: int
        """
        self.__cat_food = cat_food

    def set_dirt(self, dirt):
        """
        Сеттер для изменения кол-ва грязи в доме

        @param dirt: новое кол-во грязи
        @type dirt: int
        """
        self.__dirt = dirt
