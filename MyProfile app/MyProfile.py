# MyProfile app

SEPARATOR = '------------------------------------------'

# Personal information
name = ''
age = 0
phone_number = ''
email = ''
postcode = ''
postal_address = ''
additional_information = ''

# Information about the entrepreneur
OGRNIP = ''
INN = ''
payment_account = ''
BIC = ''
correspondent_account = ''


def personal_info_user(user_name: str, user_age: int, user_phone_number: str, user_email: str, user_postcode: int,
                       user_postal_address: str, user_additional_information: str) -> None:
    """
    Выводит личную информацию о предпринимателе:
    Имя
    Возраст
    Номер телефона
    E-mail
    Почтовый индекс
    Почтовый адрес
    Дополнительную информацию (при ее наличии)
    """

    if 11 <= user_age % 100 <= 19:
        years_parameter = 'лет'
    elif user_age % 10 == 1:
        years_parameter = 'год'
    elif 2 <= user_age % 10 <= 4:
        years_parameter = 'года'
    else:
        years_parameter = 'лет'

    print(SEPARATOR)
    print('Имя:    ', user_name)
    print('Возраст:', user_age, years_parameter)
    print('Телефон:', user_phone_number)
    print('E-mail: ', user_email)
    print('Индекс: ', user_postcode)
    print('Адрес: ', user_postal_address)
    if user_additional_information:
        print(f'\nДополнительная информация:\n{user_additional_information}')


print('Приложение MyProfile')
print('Сохраняй информацию о себе и выводи ее в разных форматах')

while True:
    # main menu
    print(SEPARATOR)
    print('ГЛАВНОЕ МЕНЮ')
    print('1 - Ввести или обновить информацию')
    print('2 - Вывести информацию')
    print('0 - Завершить работу')

    option_main_menu = int(input('Введите номер пункта меню: '))
    if option_main_menu == 0:
        break
    if option_main_menu == 1:
        # submenu 1: edit info
        while True:
            print(SEPARATOR)
            print('ВВЕСТИ ИЛИ ОБНОВИТЬ ИНФОРМАЦИЮ')
            print('1 - Личная информация')
            print('2 - Информация о предпринимателе')
            print('0 - Назад')

            option_edit_info = int(input('Введите номер пункта меню: '))
            if option_edit_info == 0:
                break
            if option_edit_info == 1:
                # input personal info
                name = input('Введите имя: ')

                while True:
                    # Validate user age
                    age = int(input('Введите возраст: '))
                    if age > 0:
                        break
                    print('Возраст должен быть положительным')
                while True:
                    # Validate user phone number
                    phone_number = input('Введите номер телефона (+7ХХХХХХХХХХ): ')
                    flag = True
                    for symbol in phone_number:
                        flag = ((symbol == '+' or '0' <= symbol <= '9') and len(phone_number) == 12) and flag
                    if flag:
                        break
                    print('Введенный номер телефона некорректный!')
                email = input('Введите адрес электронной почты: ')
                postcode = int(input('Введите почтовый индекс: '))
                postal_address = input('Введите почтовый адрес (без индекса): ')
                additional_information = input('Введите дополнительную информацию:\n')
                print('ДАННЫЕ УСПЕШНО СОХРАНЕНЫ.')
            elif option_edit_info == 2:
                # Input information about the entrepreneur
                while True:
                    OGRNIP = (input('Введите ОГРНИП: '))
                    flag = True
                    for digit in OGRNIP:
                        flag = (digit in '0123456789' and len(OGRNIP) == 15) and flag
                    if flag:
                        OGRNIP = int(OGRNIP)
                        break
                    print('ОГРНИП должен содержать 15 цифр')
                INN = int(input('Введите номер ИНН: '))
                while True:
                    payment_account = (input('Введите расчётный счёт: '))
                    flag = True
                    for digit in payment_account:
                        flag = (digit in '0123456789' and len(payment_account) == 20) and flag
                    if flag:
                        payment_account = int(payment_account)
                        break
                    print('Расчётный счёт должен содержать 20 цифр.')
                bank_name = input('Введите название банка: ')
                BIC = int(input('Введите номер БИК: '))
                correspondent_account = int(input('Введите корреспондентский счёт: '))
                print('ДАННЫЕ УСПЕШНО СОХРАНЕНЫ.')
            else:
                print('Введите корректный пункт меню')

    elif option_main_menu == 2:
        # submenu 2: print info
        while True:
            print(SEPARATOR)
            print('ВЫВЕСТИ ИНФОРМАЦИЮ')
            print('1 - Личная информация')
            print('2 - Вся информация')
            print('0 - Назад')

            option_output_info = int(input('Введите номер пункта меню: '))
            if option_output_info == 0:
                break
            if option_output_info == 1:
                personal_info_user(name, age, phone_number, email, postcode, postal_address,
                                   additional_information)
            elif option_output_info == 2:
                personal_info_user(name, age, phone_number, email, postcode, postal_address,
                                   additional_information)
                print('\nИнформация о предпринимателе')
                print(f'ОГРНИП: {OGRNIP}\nИНН: {INN}')
                print('Банковские реквизиты')
                print(f'Р/с: {payment_account}\nБанк: {bank_name}\nБИК: {BIC}\nК/с: {correspondent_account}')
            else:
                print('Введите корректный пункт меню')

    else:
        print('Введите корректный пункт меню')
