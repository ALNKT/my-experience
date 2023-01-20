def record_vitals(characters, day, my_house):
    """
    Записываем промежуточные итоги (ежедневные) о персонажах в файл

    @param my_house: дом, в котором все живут
    @type my_house: class
    @param characters: список персонажей
    @type characters: list
    @param day: номер дня
    @type day: int
    """
    with open('vitals.txt', 'a', encoding='utf-8') as file:
        file.write('--- День {} ---'.format(day).center(50))
        for i_characters in characters:
            file.write(str(i_characters) + '\n')
        file.write(f'\nЕды в холодильнике: {my_house.get_fridge()}\nКорма для кота: {my_house.get_cat_food()}\n'
                   f'Грязи в доме: {my_house.get_dirt()}\n\n\n')
