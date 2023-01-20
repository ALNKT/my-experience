from peoples import House, Husband, Wife
from pets import Cat
from functions import *


def start(characters, my_house):
    """
    Начинаем игру. Запускается цикл, который работает до тех пор, пока показатели персонажей в норме и
    не пройдет один год с начала игры

    @param my_house: дом, в котором все живут
    @type my_house: class
    @param characters: список персонажей
    @type characters: list
    """
    num_day = 0
    life = True
    while life and num_day < 365:
        num_day += 1
        print(f'\n{("--- День" + str(num_day) + "-й: ---").center(50)}', end='')
        house.set_dirt(house.get_dirt() + 5)
        for i_character in characters:
            life = i_character.life(my_house)
            if life:
                i_character.one_action()
            else:
                break
        record_vitals(characters, num_day, my_house)


house = House()
husband = Husband('Вова', house_of_husband=house)
wife = Wife('Лена', house_of_wife=house)
cat = Cat('Васька', owner=wife, cat_house=house)

wife.set_husband(husband)
husband.set_wife(wife)

my_characters = [husband, wife, cat]

start(my_characters, house)

for i_char in my_characters:
    print(i_char)
print(house)
