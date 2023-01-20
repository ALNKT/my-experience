from house import House
from time import sleep
import random


class People:
    """
    Базовый класс Человек

    __total_earned: общее количество заработанных денег
    __total_eat: общее количество съеденной еды
    __total_coat: общее количество купленных шуб
    __total_money_spent: общее кол-во потраченных денег

    Args:
        name (str): имя человека
        satiety (int): степень сытости человека
        happiness (int): степень счастья человека
        my_house (class): дом, в котором живет человек
    Attributes:
        earned (int): уровень зарплаты человека
    """
    earned = 150
    __total_earned = 0
    __total_eat = 0
    __total_coat = 0
    __total_money_spent = 0

    def __init__(self, name, satiety=30, happiness=100, my_house=House()):
        self.__name = name
        self.__satiety = satiety
        self.__happiness = happiness
        self.__house = my_house

    def get_total_earned(self):
        """
        Геттер для получения общего кол-ва заработанных денег
        @return: __total_earned
        @rtype: int
        """
        return self.__total_earned

    def get_total_eat(self):
        """
        Геттер для получения общего кол-ва съеденной еды
        @return: __total_eat
        @rtype: int
        """
        return self.__total_eat

    def get_total_coat(self):
        """
        Геттер для получения общего кол-ва купленных шуб
        @return: __total_coat
        @rtype: int
        """
        return self.__total_coat

    def get_total_money_spent(self):
        """
        Геттер для получения общего кол-ва потраченных денег
        @return: __total_money_spent
        @rtype: int
        """
        return self.__total_money_spent

    def get_name(self):
        """
        Геттер для получения имени человека

        @return: __name
        @rtype: str
        """
        return self.__name

    def get_satiety(self):
        """
        Геттер для получения уровня сытости человека

        @return: __satiety
        @rtype: int
        """
        return self.__satiety

    def get_happiness(self):
        """
        Геттер для получения уровня счастья человека

        @return: __happiness
        @rtype: int
        """
        return self.__happiness

    def get_house(self):
        """
        Геттер для получения дома, в котором живет человек

        @return: __house
        @rtype: class
        """
        return self.__house

    def set_total_earned(self, amount_earned):
        """
        Сеттер для изменения общего кол-ва заработанных денег

        @param amount_earned: кол-во денег
        @type amount_earned: int
        """
        self.__total_earned += amount_earned

    def set_total_eat(self, amount_eat):
        """
        Сеттер для изменения общего кол-ва съеденной еды
        @param amount_eat: кол-во еды
        @type amount_eat: int
        """
        self.__total_eat += amount_eat

    def set_total_coat(self, amount_coat):
        """
        Сеттер для получения общего кол-ва купленных шуб
        @param amount_coat: кол-во шуб
        @type amount_coat: int
        """
        self.__total_coat += amount_coat

    def set_total_money_spent(self, amount_money):
        """
        Сеттер для получения общего потраченных денег
        @param amount_money: кол-во потраченных денег
        @type amount_money: int
        """
        self.__total_money_spent += amount_money

    def set_name(self, name):
        """
        Сеттер для изменения имени человека

        @param name: новое имя человека
        @type name: str
        """
        self.__name = name

    def set_satiety(self, satiety):
        """
        Сеттер для изменения уровня сытости человека

        @param satiety: новый уровень сытости человека
        @type satiety: int
        """
        self.__satiety = satiety

    def set_happiness(self, happiness):
        """
        Сеттер для изменения уровня счастья человека

        @param happiness: новый уровень счастья человека
        @type happiness: int
        """
        self.__happiness = happiness

    def __str__(self):
        return ('\nИмя: {name}\nУровень сытости: {satiety}\nУровень счастья: {happiness}\nДом: {house}\n'
                'Было заработано денег: {money} руб.\nПотрачено денег: {spent} руб.\nСъедено еды: {food} кг.\n'
                'Куплено шуб: {coat} шт.'.
                format(name=self.__name, satiety=self.__satiety, happiness=self.__happiness,
                       house=self.__house.get_name(), money=self.__total_earned, spent=self.__total_money_spent,
                       food=self.__total_eat, coat=self.__total_coat))

    def eat(self):
        """
        Человек отправляется трапезничать. При этом рандомно увеличивается сытость человека
        и на такое же кол-во уменьшаются запасы еды в холодильнике

        @return: Если еды достаточно в холодильнике, человек ест. Возвращается True, иначе False
        @rtype: boolean
        """

        amount_of_food = random.randint(1, 30)
        if self.__house.get_fridge() >= amount_of_food:
            print(f'\n{self.__name} ест...')
            for _ in range(7):
                sleep(0.2)
                print('🍰 ', end=' ')
            sleep(0.2)
            self.__satiety += amount_of_food
            self.__house.set_fridge(self.__house.get_fridge() - amount_of_food)
            self.__total_eat += amount_of_food
            print(f'{self.get_name()}: "Какая вкусная еда!".\nТекущий уровень сытости: {self.__satiety}')
            return True
        return False

    def stroking_the_cat(self):
        """
        Погладить кота. При этом растет уровень счастья на 5 пунктов
        """
        if self.__satiety > 10:
            print(f'\n{self.__name} говорит: "Какое счастье, погладить кота!"')
            self.__satiety -= 10
            self.__happiness += 20
        else:
            print(f'{self.get_name()} кричит: "Я хочу есть!"')
            self.eat()

    def one_action(self):
        """
        Совершаем одно действие персонажем
        @return: если персонаж поел, то возвращаем True, иначе False
        @rtype: boolean
        """
        if self.__satiety < 20:
            self.eat()
            return True
        return False

    def life(self, my_house):
        """
        Определяем жив ли персонаж. Если сытость падает ниже 0 или счастье ниже 10, то персонаж умирает.
        Также тут проверяем кол-во грязи в доме, если оно больше 90 пунктов, то счастье персонажа падает на 10

        @return: False, если персонаж умер, True, если жив
        @rtype: boolean
        """
        if my_house.get_dirt() > 90:
            self.__happiness -= 10
        if self.__satiety < 0 or self.__happiness < 10:
            return False
        return True


class Husband(People):
    """
    Класс Муж

    Args:
        name (str): Имя мужа
        satiety (int): степень сытости мужа
        happiness (int): степень счастья мужа
        house_of_husband (class): дом, в котором живет муж
    """

    def __init__(self, name, satiety=30, happiness=100, house_of_husband=House(), my_wife=None):
        super().__init__(name, satiety, happiness, house_of_husband)
        self.__wife = my_wife

    def set_wife(self, my_wife):
        """
        Сеттер для установки значения аргумента __wife

        @param my_wife: новая жена
        @type my_wife: class
        """
        self.__wife = my_wife

    def eat(self):
        """
        Человек отправляется трапезничать. При этом вызывается функция родительского класса, где
        рандомно увеличивается сытость человека
        и на такое же кол-во уменьшаются запасы еды в холодильнике
        Если попытка поесть неуспешная, т.е. еды недостаточно, то отправляем жены в магазин за продуктами
        """

        if not super().eat():
            print(
                f'{self.get_name()} кричит: "У нас нет еды! {self.__wife.get_name()}! '
                f'Срочно беги в магазин за продуктами!"')
            self.__wife.run_for_food()

    def playing(self):
        """
        Человек отправляется играть в компьютерные игры. Увеличивается счастье на 10 и уменьшается сытость на 10
        Если сытости не хватает, то отправляемся есть
        """
        games = ['God of War', 'Uncharted', 'Косынку', 'Солитер', 'Покер']
        if self.get_satiety() > 10:
            self.set_satiety(self.get_satiety() - 10)
            self.set_happiness(self.get_happiness() + 20)
            game = random.choice(games)
            print(f'\n{self.get_name()} решил поиграть в {game}!')
            for _ in range(7):
                sleep(0.2)
                print('🎮 ', end=' ')
            sleep(0.2)
            print(
                f'{self.get_name()}: "Обожаю эту игру! Теперь я стал счастливее!"\n'
                f'Текущий уровень счастья: {self.get_happiness()}!')
        else:
            print(f'{self.get_name()}: "Я голоден!!! Быстрее к холодильнику!"')
            self.eat()

    def working(self):
        """
        Человек отправляется на работу. При этом уменьшается сытость на 10 и человек зарабатывает деньги.
        Уровень зарплаты устанавливается в родительском классе.
        Если сытости недостаточно, то отправляемся есть.
        """
        if self.get_satiety() > 10:
            print(f'\n{self.get_name()} приступает к тяжелому труду...')
            for _ in range(7):
                sleep(0.2)
                print('🔨 ', end=' ')
            sleep(0.2)
            self.set_satiety(self.get_satiety() - 10)
            self.get_house().set_money(self.get_house().get_money() + People.earned)
            self.set_total_earned(People.earned)
            print('Работа завершена! Сытость упала на 10. Заработано {} руб. '
                  '\nНаш бюджет: {}    {}, уровень сытости: {}'.
                  format(People.earned, self.get_house().get_money(), self.get_name(), self.get_satiety()))
        else:
            print(f'{self.get_name()} кричит: "У меня нет сил работать! Нужно срочно поесть!"')
            self.eat()

    def one_action(self):
        """
        Совершаем одно действие персонажем.
        Проверяем кол-во денег в доме, уровень счастья и выполняем одно из двух либо любое другое действие
        """
        if not super().one_action():
            if self.get_house().get_money() < 150:
                self.working()
            elif self.get_happiness() < 10:
                self.playing()
            else:
                actions = ['eat', 'one_action', 'playing', 'stroking_the_cat', 'working']
                getattr(self, random.choice(actions))()


class Wife(People):
    """
    Класс Жена

    Args:
        name (str): имя жены
        satiety (int): степень сытости жены
        happiness (int): степень счастья жены
        house_of_wife (class): дом, в котором живет жена
    """

    def __init__(self, name, satiety=30, happiness=100, house_of_wife=House(), my_husband=None):
        super().__init__(name, satiety, happiness, house_of_wife)
        self.__husband = my_husband

    def set_husband(self, my_husband):
        """
        Сеттер для установки значения аргумента __husband

        @param my_husband: новый муж
        @type my_husband: class
        """
        self.__husband = my_husband

    def run_for_food(self):
        """
        Поход жены за продуктами в магазин. Поход возможен, если уровень сытости больше 10 и в доме больше 10 рублей.
        При этом сытость падает на 10 и денег уменьшается на 10.
        Если еды не хватает, то отправляемся есть. Если денег не хватает, то оправляем мужа работать
        """
        if self.get_satiety() > 10 and self.get_house().get_money() > 60:
            self.set_satiety(self.get_satiety() - 10)
            print(f'\n{self.get_name()} кричит: "Я побежала в магазин за продуктами!!!"')
            for _ in range(7):
                sleep(0.2)
                print('🛒 ', end=' ')
            sleep(0.2)
            self.get_house().set_fridge(self.get_house().get_fridge() + 60)
            print(f'{self.get_name()} купила нам еды на 60 руб.\n'
                  f'Теперь у нас в холодильнике {self.get_house().get_fridge()} еды!')
            self.set_total_money_spent(60)
            self.get_house().set_money(self.get_house().get_money() - 60)
        elif self.get_satiety() <= 10:
            print(f'{self.get_name()} кричит: "У меня нет сил идти в магазин! Нужно срочно поесть!"')
            self.eat()
        elif self.get_house().get_money() <= 60:
            print(f'{self.get_name()} кричит: "У нас нет денег на продукты! {self.__husband.get_name()}, '
                  f'срочно отправляйся на работу!"')
            self.__husband.working()

    def buy_cat_food(self):
        """
        Покупка женой корма для кота.
        Если достаточно сил и денег, то покупаем корм, иначе сообщаем, что чего-то не хватает
        """
        if self.get_satiety() > 10 and self.get_house().get_money() > 10:
            self.set_satiety(self.get_satiety() - 10)
            print(f'\n{self.get_name()} кричит: "{self.__husband.get_name()}, я побежала за кормом для кота!!!"')
            for _ in range(7):
                sleep(0.2)
                print('🛒 ', end=' ')
            sleep(0.2)
            self.get_house().set_cat_food(self.get_house().get_cat_food() + 10)
            print(f'{self.get_name()} купила корм коту на 10 руб.\n'
                  f'Теперь у нас в доме {self.get_house().get_cat_food()} корма!')
            self.get_house().set_money(self.get_house().get_money() - 10)
            self.set_total_money_spent(10)
        elif self.get_satiety() <= 10:
            print(f'{self.get_name()} кричит: "У меня нет сил идти в магазин! Нужно срочно поесть!"')
            self.eat()
        elif self.get_house().get_money() <= 10:
            print(f'{self.get_name()} кричит: "У нас нет денег на корм для кота! {self.__husband.get_name()}, '
                  f'срочно отправляйся на работу!"')
            self.__husband.working()

    def buy_coat(self):
        """
        Поход жены за шубой в магазин. Поход возможен, если уровень сытости больше 10 и в доме больше 350 рублей.
        При этом сытость падает на 10 и денег уменьшается на 350.
        Если еды не хватает, то отправляемся есть. Если денег не хватает, то оправляем мужа работать
        """
        if self.get_satiety() > 10 and self.get_house().get_money() >= 350:
            print(f'\n{self.get_name()} кричит: "{self.__husband.get_name()}, я пошла покупать себе шубу!"')
            for _ in range(7):
                sleep(0.2)
                print('🧥 ', end=' ')
            sleep(0.2)
            self.set_satiety(self.get_satiety() - 10)
            self.get_house().set_money(self.get_house().get_money() - 350)
            self.set_happiness(self.get_happiness() + 60)
            self.set_total_coat(1)
            self.set_total_money_spent(350)
            print(f'{self.get_name()}: "Я купила себе прекрасную шубу! Правда дороговато... 350 руб."')
        elif self.get_satiety() <= 10:
            print(f'{self.get_name()} кричит: "У меня нет сил добежать до магазина! Нужно срочно поесть!"')
            self.eat()
        elif self.get_house().get_money() <= 350:
            print(f'{self.get_name()} кричит: "У нас нет денег на шубу!! {self.__husband.get_name()}, '
                  f'срочно отправляйся на работу!"')
            self.__husband.working()

    def cleaning(self):
        """
        Уборка в доме. Генерируется случайное количество убранной грязи. Если сил на уборку нет, то жена идет есть
        """
        if self.get_satiety() > 10:
            amount_of_dirt = random.randint(5, 100)
            print(f'\n{self.get_name()} кричит: "{self.__husband.get_name()}, я пошла убираться в доме!"')
            for _ in range(7):
                sleep(0.2)
                print('🧹 ', end=' ')
            sleep(0.2)
            self.set_satiety(self.get_satiety() - 10)
            self.get_house().set_dirt(self.get_house().get_dirt() - amount_of_dirt)
            self.get_house().set_total_dirt(amount_of_dirt)
            print(f'{self.get_name()}: "Как же я устала убираться. Но в доме стало чище на {amount_of_dirt}%!"')
        else:
            print(f'{self.get_name()}: "У меня нет сил убираться. Нужно срочно подкрепиться!"')
            self.eat()

    def eat(self):
        """
        Человек отправляется трапезничать. При этом вызывается функция родительского класса, где
        рандомно увеличивается сытость человека
        и на такое же кол-во уменьшаются запасы еды в холодильнике
        Если попытка поесть неуспешная, т.е. еды недостаточно, то отправляем жены в магазин за продуктами
        """
        if not super().eat():
            print(
                f'{self.get_name()} кричит: "У нас нет еды! {self.__husband.get_name()}! '
                f'Я побежала в магазин за продуктами!"')
            self.run_for_food()

    def one_action(self):
        """
        Совершаем одно действие персонажем.
        Проверяем кол-во еды в доме, кол-во корма для кота, уровень счастья и уровень грязи в доме.
        Выполняем одно из соответствующих действий, либо любое другое действие
        """
        if not super().one_action():
            if self.get_house().get_fridge() < 60:
                self.run_for_food()
            elif self.get_house().get_cat_food() < 10:
                self.buy_cat_food()
            elif self.get_happiness() < 10:
                self.buy_coat()
            elif self.get_house().get_dirt() > 50:
                self.cleaning()
            else:
                actions = ['buy_cat_food', 'buy_coat', 'cleaning', 'eat', 'one_action', 'run_for_food',
                           'stroking_the_cat']
                getattr(self, random.choice(actions))()
