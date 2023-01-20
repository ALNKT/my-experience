from house import House
import random
from time import sleep


class Pet:
    """
    Базовый класс домашние животные

    __total_cat_food (int): общее количество съеденного корма животным

    Args:
        name (str): имя животного
        satiety (int): степень сытости животного
        cat_house (class): дом, в котором живет животное
    """
    __total_cat_food = 0

    def __init__(self, name, owner, satiety=30, cat_house=House()):
        self.__name = name
        self.__satiety = satiety
        self.__cat_house = cat_house
        self.__owner = owner

    def __str__(self):
        return f'\nИмя: {self.__name}\nСытость: {self.__satiety}'

    def get_name(self):
        """
        Геттер для получения имени домашнего животного

        @return: __name
        @rtype: str
        """
        return self.__name

    def get_satiety(self):
        """
        Геттер для получения уровня сытости домашнего животного

        @return: __satiety
        @rtype: int
        """
        return self.__satiety

    def get_cat_house(self):
        """
        Геттер для получения дома животного

        @return: __cat_house
        @rtype: class
        """
        return self.__cat_house

    def get_total_cat_food(self):
        """
        Геттер для получения общего кол-ва съеденного корма
        @return: __total_cat_food
        @rtype: int
        """
        return self.__total_cat_food

    def set_total_cat_food(self, cat_food):
        """
        Сеттер для установки съеденного корма

        @param cat_food: кол-во съеденного корма
        @type cat_food:
        """
        self.__total_cat_food += cat_food

    def set_satiety(self, satiety):
        """
        Сеттер для установки нового значения сытости животного

        @param satiety: новая сытость
        @type satiety: int
        """
        self.__satiety = satiety

    def eat(self):
        """
        Кормление кота. Если корма в доме достаточно, кот ест, иначе отправляет хозяев за кормом.
        Генерируется случайное кол-во корма от 1 до 10 (включительно), которое животное съедает
        """
        if self.__cat_house.get_cat_food() > 10:
            amount_of_food = random.randint(1, 10)
            print(f'\n{self.__name} ест...')
            for _ in range(7):
                sleep(0.2)
                print('🍲 ', end=' ')
            sleep(0.2)
            self.__satiety += amount_of_food * 2
            self.__cat_house.set_cat_food(self.__cat_house.get_cat_food() - amount_of_food)
            self.__total_cat_food += amount_of_food
            print(f'{self.__name}: "Мяу".\n{self.__name} накормлен, текущий уровень сытости: {self.__satiety}')
        else:
            print(f'{self.__name} голоден! Корма нет! нужно купить!')
            self.__owner.buy_cat_food()

    def sleep(self):
        """
        Персонаж ложится спать
        Сытость уменьшается на 10
        """
        if self.__satiety > 10:
            print(f'\nНаш {self.__name} решил вздремнуть.')
            self.__satiety -= 10
        else:
            print(f'Наш {self.__name} не может спать! Его нужно покормить')
            self.eat()

    def life(self):
        """
        Определяем жив ли персонаж. Если сытость падает ниже 0 или счастье ниже 10, то персонаж умирает.
        Также тут проверяем кол-во грязи в доме, если оно больше 90 пунктов, то счастье персонажа падает на 10

        @return: False, если персонаж умер, True, если жив
        @rtype: boolean
        """
        if self.__satiety < 0:
            return False
        return True

    def one_action(self):
        """
        Совершаем одно действие персонажем.
        Проверяем сытость, если персонаж голоден, то отправляем есть.
        @return: True, если персонаж отправился есть, иначе False
        @rtype: boolean
        """
        if self.__satiety < 10:
            self.eat()
            return True
        return False


class Cat(Pet):
    """
    Класс кот. Родительский класс Pet

    Args:
        name (str): имя кота
        satiety (int): степень сытости кота
        cat_house (class): дом, в котором живет кот
    """

    def __init__(self, name, owner, satiety=30, cat_house=House()):
        super().__init__(name, owner, satiety, cat_house)

    def tear_up_the_wallpaper(self):
        """
        Кот дерет обои. При это сытость кота уменьшается на 10, а грязь в доме увеличивается на 5
        """
        if self.get_satiety() > 10:
            print(f'\nНаш {self.get_name()} дерет обои!')
            self.set_satiety(self.get_satiety() - 10)
            self.get_cat_house().set_dirt(self.get_cat_house().get_dirt() + 5)
            self.get_cat_house()
            self.get_cat_house().set_total_dirt(5)
        else:
            print(f'Наш {self.get_name()} голоден! Его нужно покормить')
            self.eat()

    def one_action(self):
        """
        Совершаем одно случайное действие котом.
        """
        if not super().one_action():
            actions = ['eat', 'sleep', 'tear_up_the_wallpaper']
            getattr(self, random.choice(actions))()
