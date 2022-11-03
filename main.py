import datetime
from datetime import date
import psycopg2
from psycopg2 import sql
import random
import transliterate


def create_tables(connection):
    """
    Создает таблицы
    :param connection: На вход получает соединение с базой данных
    :return: Ничего не возвращает (надо бы подумать над обработкой исключений)
    """

    with connection.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS person("
                    "person_id SERIAL PRIMARY KEY,"
                    "first_name VARCHAR(40) NOT NULL,"
                    "second_name VARCHAR(50) NOT NULL,"
                    "third_name VARCHAR(50),"
                    "date_of_birth DATE NOT NULL CHECK (date_of_birth <= CURRENT_DATE));")

        cur.execute("CREATE TABLE IF NOT EXISTS phone_number("
                    "phone_num_full VARCHAR(15) NOT NULL,"
                    "person_id INTEGER NOT NULL,"
                    "PRIMARY KEY (phone_num_full, person_id),"
                    "FOREIGN KEY (person_id)"
                    "    REFERENCES person (person_id));")

        cur.execute("CREATE TABLE IF NOT EXISTS email_address("
                    "email_full VARCHAR(250) NOT NULL,"
                    "person_id INTEGER NOT NULL,"
                    "PRIMARY KEY (email_full, person_id),"
                    "FOREIGN KEY (person_id)"
                    "    REFERENCES person (person_id));")

        connection.commit()


def make_third_name(first_name, sex):
    """
    Делает из имени отчество
    :param first_name: Имя
    :param sex: 'm' - мужчина или 'f' - женщина
    :return: Отчество
    """

    if sex == 'm':
        if first_name[-2:len(first_name)] == 'рж':
            third_name = first_name + 'евич'
        elif first_name[-2:len(first_name)] == 'ей':
            third_name = first_name[:-1] + 'евич'
        else:
            third_name = first_name + 'ович'
    else:
        if first_name[-2:len(first_name)] == 'рж':
            third_name = first_name + 'евна'
        elif first_name[-2:len(first_name)] == 'ей':
            third_name = first_name[:-1] + 'евна'
        else:
            third_name = first_name + 'овна'

    return third_name


def generate_phone_num():
    """
    Генерирует номер телефона, состоящий из 11 - 15 цифр
    :return: Возвращает строку номера
    """
    phone_num = ''
    phone_num_len = random.randrange(11, 16)

    for i in range(phone_num_len):
        if i == 0:
            phone_num += str(random.randrange(1, 10))
        else:
            phone_num += str(random.randrange(0, 10))

    return phone_num


def generate_email_address(s_name, f_name, t_name):
    """
    Генерирует email адрес, используя имя, фамилию, отчество и список доменов
    Для переданных имени и фамилии выполняется транслитерация
    :param f_name: Имя
    :param s_name: Фамилия
    :param t_name: Отчество
    :return: Возвращает строку email адреса
    """
    domain_list = ['mail.ru', 'gmail.com', 'yandex.ru', 'ya.ru', 'hotmail.com', 'rambler.ru', 'yahoo.com', 'mail.com',
                   'outlook.com', 'protonmail.com']

    choice = random.randrange(1, 6)

    if choice == 1:
        email_address = f'{f_name[0]}.{t_name[0]}.{s_name}@{random.choice(domain_list)}'
    elif choice == 2:
        email_address = f'{f_name[0]}-{t_name[0]}-{s_name}@{random.choice(domain_list)}'
    elif choice == 3:
        email_address = f'{f_name[0]}_{t_name[0]}_{s_name}@{random.choice(domain_list)}'
    elif choice == 4:
        email_address = f'{f_name}.{s_name}@{random.choice(domain_list)}'
    elif choice == 5:
        email_address = f'{f_name}-{s_name}@{random.choice(domain_list)}'
    elif choice == 6:
        email_address = f'{f_name}_{s_name}@{random.choice(domain_list)}'

    return transliterate.translit(email_address, reversed=True).lower()


def generate_data(sex):
    """
    Генерирует кортеж данных одного клиента из заранее подготовленных списков
    На вход принимает строку из одного символа, соответствующую полу клиента - 'm' - мужчина, 'f' - женщина
    :return: Возвращает кортеж с данными в формате first_name, second_name, third_name, date_of_birth,
             phone_num_full, email_full
    """

    male_first_name_list = ['Алексей', 'Егор', 'Федор', 'Михаил', 'Петр', 'Сергей', 'Марк', 'Степан', 'Андрей', 'Жорж']
    female_first_name_list = ['Арина', 'Мария', 'Злата', 'Петра', 'Светлана', 'Ирина', 'Жанна', 'Виктория', 'Екатерина',
                              'Татьяна']
    male_second_name_list = ['Иванов', 'Петров', 'Сидоров', 'Кузнецов', 'Смирнов', 'Попов', 'Соколов', 'Михайлов',
                             'Васильев', 'Федоров']

    if sex == 'm':
        first_name = random.choice(male_first_name_list)
        third_name = make_third_name(random.choice(male_first_name_list), 'm')
        second_name = random.choice(male_second_name_list)
    elif sex == 'f':
        first_name = random.choice(female_first_name_list)
        third_name = make_third_name(random.choice(male_first_name_list), 'f')
        second_name = random.choice(male_second_name_list) + 'а'

    date_of_birth = str(datetime.date(random.randrange(1960, 2022), random.randrange(1, 13), random.randrange(1, 29)))
    phone_num_full = generate_phone_num()
    email_full = generate_email_address(second_name, first_name, third_name)

    return first_name, second_name, third_name, date_of_birth, phone_num_full, email_full


def print_table(table_list):
    """
    Печатает таблицу в красивом виде
    :param table_list: Список кортежей с записями для печати
                       Формат записи: (id, fname, sname, tname, date_of_birth, phone_num, email_address)
    """

    lengths = [8, 16, 20, 20, 20, 25, 35]
    columns = ['ID', 'Имя', 'Отчество', 'Фамилия', 'Дата рождения', 'Номер телефона', 'email']

    print()
    print((8 + sum(lengths)) * '-')
    for i, column in enumerate(columns):
        print('|{:^{width}}'.format(column, width=lengths[i]), end='')
    print('|')
    print((8 + sum(lengths)) * '-')

    for row in table_list:
        # print(row)
        for i in range(4):
            # print(row[i])
            if row[i] is not None:
                print('|{:^{width}}'.format(row[i], width=lengths[i]), end='')
            else:
                print('|{:^{width}}'.format('', width=lengths[i]), end='')
        print('|{:^{width}}'.format(date.isoformat(row[4]), width=lengths[4]), end='')
        for i in range(5, 7):
            if row[i] is not None:
                print('|{:^{width}}'.format(row[i], width=lengths[i]), end='')
            else:
                print('|{:^{width}}'.format('', width=lengths[i]), end='')
        print('|')

    print((8 + sum(lengths)) * '-')


def insert_phone_num_for_existing_client(connection, phone_number, person_id):
    """
    Добавляет в таблицу phone_number запись с номером телефона существующего клиента, имеющего person_id
    :param connection: Получает открытое соединение с базой данных
    :param phone_number: Получает номер телефона. Должен быть строкой ненулевой длины
    :param person_id: Получает id клиента из таблицы person
    :return: Ничего не возвращает
    """
    with connection.cursor() as cur:
        if isinstance(phone_number, str) and phone_number.isdigit() and len(phone_number) > 0:
            # В базу данных вносятся только текстовые ненулевые данные, содержащие только цифры
            cur.execute("INSERT INTO phone_number(phone_num_full, person_id)"
                        "VALUES (%s, %s);", (phone_number, person_id))
            connection.commit()


def check_email_address(email_str):
    """
    Выполняет простейшую проверку того, что email_str похож на адрес email
    :param email_str: строка для проверки
    :return: TRUE если проверка пройдена FALSE если не пройдена
    """
    if len(email_str) >= 6 and email_str.count('@') == 1 and email_str.count('@', 1, -4) == 1 \
            and email_str.count('.', -5, -1) == 1:
        return True
    else:
        print(f'Адрес "{email_str}" скорее всего не является адресом электронной почты')
        return False


def insert_email_for_existing_client(connection, email_address, person_id):
    """
    Добавляет в таблицу email_address запись с номером телефона существующего клиента, имеющего person_id
    :param connection: Получает открытое соединение с базой данных
    :param email_address: Получает email адрес. Должен быть строкой ненулевой длины
    :param person_id: Получает id клиента из таблицы person
    :return: Ничего не возвращает
    """
    with connection.cursor() as cur:
        if isinstance(email_address, str) and len(email_address) > 0 and check_email_address(email_address):
            # В базу данных вносятся только текстовые ненулевые данные, в который присутствует
            # символ '@' и длина минимально достаточна для формирования адреса email
            # Как понял, проверка адреса email это не такая уж тривиальая задача,
            # поэтому сделал простейшую проверку, чтобы адрес просто был похож на email
            cur.execute("INSERT INTO email_address(email_full, person_id)"
                        "VALUES (%s, %s);", (email_address, person_id))
            connection.commit()
        else:
            print('Адрес электронной почты не будет добавлен')


def insert_new_client_data(connection, data_tup, output=True):
    """
    Добавляет во все таблицы данные нового клиента
    :param connection: Получает соединение с базой данных
    :param data_tup: Кортеж в формате first_name, second_name, third_name, date_of_birth, phone_num_full,
                           email_full
    :return: Ничего не возвращает
    """

    with connection.cursor() as cur:
        cur.execute("INSERT INTO person(first_name, second_name, third_name, date_of_birth)"
                    "VALUES (%s, %s, %s, %s);", data_tup[0:4])

        # Запрос person_id новой записи клиента для заполнения таблиц телефонов и email
        cur.execute("SELECT person_id "
                    "FROM person "
                    "ORDER BY person_id DESC "
                    "LIMIT 1;")

        new_person_id = cur.fetchone()[0]

        connection.commit()

        # Добавление телефона и email коммитится в своих функциях
        insert_phone_num_for_existing_client(connection, data_tup[4], new_person_id)
        insert_email_for_existing_client(connection, data_tup[5], new_person_id)

        if output:
            print()
            print('Добавлен новый клиент:')
            print_table(find_client(conn, '', '', '', '', '', '', new_person_id))


def generate_select_query(param_dict_sel):
    """
    Формирует SQL-запрос на выборку из всех таблиц по переданным значениям
    :param param_dict_sel: Словарь где ключи - это названия столбцов всех таблиц,
                       а значения - это параметры для выполнения запроса
    :return: SQL-запрос в виде sql-объекта psychopg2
    """

    select_column_list = sql.SQL(', ').join(sql.Identifier(n) for n in list(param_dict_sel))

    composed_list = [sql.SQL("SELECT {} FROM person "
                             "LEFT JOIN phone_number AS pn "
                             "USING (person_id) "
                             "LEFT JOIN email_address AS ea "
                             "USING (person_id) "
                             "").format(select_column_list)]

    counter = 0

    for k, v in param_dict_sel.items():
        if v is not None and isinstance(v, str) and len(v) > 0 and k != 'date_of_birth':
            if counter == 0:
                composed_list.append(sql.SQL("WHERE {} LIKE {} ").format(sql.Identifier(k), sql.Literal(v)))
            else:
                composed_list.append(sql.SQL("AND {} LIKE {} ").format(sql.Identifier(k), sql.Literal(v)))
            counter += 1

    if counter == 0 and param_dict_sel['person_id'] is not None:
        composed_list.append(sql.SQL("WHERE {} = {} ").
                             format(sql.Identifier('person_id'), sql.Literal(param_dict_sel['person_id'])))
    elif counter != 0 and param_dict_sel['person_id'] is not None:
        composed_list.append(sql.SQL("AND {} = {} ").
                             format(sql.Identifier('person_id'), sql.Literal(param_dict_sel['person_id'])))

    if counter == 0 and param_dict_sel['date_of_birth'] is not None and param_dict_sel['person_id'] is None:
        composed_list.append(sql.SQL("WHERE {} = {} ").
                             format(sql.Identifier('date_of_birth'), sql.Literal(param_dict_sel['date_of_birth'])))
    elif counter != 0 and param_dict_sel['date_of_birth'] is not None and param_dict_sel['person_id'] is None:
        composed_list.append(sql.SQL("AND {} = {} ").
                             format(sql.Identifier('date_of_birth'), sql.Literal(param_dict_sel['date_of_birth'])))

    composed_list.append(sql.SQL("ORDER BY person_id"))

    return sql.Composed(composed_list)


def find_client(connection, fname, sname, thname, date_of_birth, phone_num, email_address, person_id=None):
    """
    Поиск клиента по имени, фамилии, отчеству, адресу электронной почты, телефону
    :return: Возвращает список кортежей с id, именем, фамилией и отчеством клиента
    """
    param_dict = {'person_id': person_id, 'first_name': fname, 'third_name': thname, 'second_name': sname,
                  'date_of_birth': date_of_birth, 'phone_num_full': phone_num, 'email_full': email_address}

    query = generate_select_query(param_dict)

    with connection.cursor() as cur:
        cur.execute(query)
        selected_data = cur.fetchall()

    return selected_data


def insert_init_data():
    """
    Заполняет таблицу данными
    """
    males_qty = random.randrange(3, 11)
    females_qty = random.randrange(3, 11)

    init_data = []

    for i in range(males_qty):
        person_data = generate_data('m')
        insert_new_client_data(conn, person_data, False)
        init_data.append(*find_client(conn, *person_data))

    for i in range(males_qty, males_qty + females_qty):
        person_data = generate_data('f')
        insert_new_client_data(conn, person_data, False)
        init_data.append(*find_client(conn, *person_data))

    conn.commit()

    print('\nДобавлено', males_qty + females_qty, 'записей')
    print_table(init_data)


def generate_update_query(param_dict_update):
    """
    Формирует SQL-запрос на изменение данных о клиенте на переданные значения
    :param param_dict_update: Словарь где ключи - это названия столбцов таблицы person,
                       а значения - это параметры для выполнения запроса
    :return: SQL-запрос в виде sql-объекта psychopg2
    """

    composed_list = [sql.SQL("UPDATE person ")]
    counter = 0

    for k, v in param_dict_update.items():
        if k != 'person_id' and v is not None and isinstance(v, str) and len(v) > 0 or isinstance(v, datetime.date):
            if counter == 0:
                composed_list.append(sql.SQL("SET {} = {} ").format(sql.Identifier(k), sql.Literal(v)))
            else:
                composed_list.append(sql.SQL(", {} = {} ").format(sql.Identifier(k), sql.Literal(v)))
            counter += 1

    composed_list.append(sql.SQL("WHERE {} = {} ").
                         format(sql.Identifier('person_id'), sql.Literal(param_dict_update['person_id'])))

    return sql.Composed(composed_list)


def update_client(connection, person_id, fname, sname, thname, date_of_birth):
    """
    Изменение данных клиента - имени, фамилии, отчества и даты рождения
    """
    param_dict_update = {'person_id': person_id, 'first_name': fname, 'third_name': thname,
                         'second_name': sname, 'date_of_birth': date_of_birth}

    found_client = find_client(connection, '', '', '', '', '', '', person_id)

    if found_client:
        query = generate_update_query(param_dict_update)

        with connection.cursor() as cur:
            cur.execute(query)

            connection.commit()
    else:
        print('Такого клиента нет')


def delete_phone_number(connection, person_id, phone_number):
    """
    Удаляет из таблицы phone_number запись с указанным person_id  и phone_number
    """
    if find_client(connection, '', '', '', '', phone_number, '', person_id):
        with connection.cursor() as cur:
            cur.execute("DELETE FROM phone_number "
                        "WHERE person_id = %s "
                        "AND phone_num_full LIKE %s;", (person_id, phone_number))
            connection.commit()
    else:
        print('Клиента с таким номером телефона нет')


def delete_email_address(connection, person_id, email_address):
    """
    Удаляет из таблицы email_address запись с указанным person_id  и email_address
    """
    if find_client(connection, '', '', '', '', '', email_address, person_id):
        with connection.cursor() as cur:
            cur.execute("DELETE FROM email_address "
                        "WHERE person_id = %s "
                        "AND email_full LIKE %s;", (person_id, email_address))
            connection.commit()
    else:
        print('Клиента с таким email нет')


def delete_client(connection, person_id):
    """
    Удаляет из таблицы person и всех связанных таблиц записи с указанным person_id
    """
    if find_client(connection, '', '', '', '', '', '', person_id):
        with connection.cursor() as cur:
            cur.execute("DELETE FROM phone_number "
                        "WHERE person_id = %s; ", (person_id,))
            cur.execute("DELETE FROM email_address "
                        "WHERE person_id = %s; ", (person_id,))
            cur.execute("DELETE FROM person "
                        "WHERE person_id = %s; ", (person_id,))
            connection.commit()
    else:
        print('Такого клиента в базе данных нет')


def input_client_info():
    """
    Выполняет ввод данных клиента - fname, sname, tname, date_of_birth, phone_num, email
    :return: кортеж введенных данных в указанном порядке
    Для корректной работы запросов к базе данных, дата рождения преобразуется в формат даты и если преобразование
    не может быть выполнено, значению присваивается значение None
    """
    print("""При вводе данных также необходимо учитывать следующее:
    - Дату рождения необходимо вводить в формате ГГГГ-ММ-ДД, например, 2022-12-31
    - Номер телефона нужно вводить без специальных символов, таких как +()
    - Электронную почту нужно вводить в формате example@mail.com""")
    print(80 * '-')
    sname = input('Введите фамилию: ')
    fname = input('Введите имя: ')
    tname = input('Введите отчество: ')
    date_of_birth = input('Введите дату рождения: ')

    if date_of_birth is not None and len(date_of_birth) == 10:
        date_of_birth = date.fromisoformat(date_of_birth)
    else:
        date_of_birth = None
        print('Введенная дата не распознана')

    phone_num = input('Введите номер телефона: ')
    email_address = input('Введите адрес электронной почты: ')

    return fname, sname, tname, date_of_birth, phone_num, email_address


def user_choice_find():
    """
    Реализует поиск клиента
    :return:
    """

    print(25 * '-', 'Поиск клиента. Краткая инструкция', 25 * '-')
    print('- Поиск клиента можно выполнить по имени, фамилии, отчеству, номеру телефона и email-адресу')
    print('- Можно ввести один из указанных параметров, несколько или все')
    print('- Если будет введено более одного параметра, то условие поиска будет включать все введенные параметры,')
    print('  то есть будут найдены только те клиенты, у которых все введенные параметры будут равны соответствующим значениям')
    print('- Если какой-то из параметров вводить не нужно, просто нажмите ввод и переходите к вводу следующего')
    print('- Для замены одного или нескольких символов в поисковом параметре можно указать символы %%')
    print(80 * '-')

    fname ,sname, tname, date_of_birth, phone_num, email_address = input_client_info()

    search_result = find_client(conn, fname, sname, tname, date_of_birth, phone_num, email_address)

    if search_result:
        print_table(search_result)
    else:
        print()
        print('По вашему запросу ничего не найдено')


def user_choice_add_new_client():
    """
    Функция добавления нового клиента
    :return:
    """

    print()
    print('Для добавления нового клиента ввод имени, фамилии и даты рождения обязательны')
    new_client = input_client_info()
    if new_client[0] and new_client[1] and new_client[3]:
        insert_new_client_data(conn, new_client)
    else:
        print('\nНе все необходимые данные введены, ничего не добавлено')


def user_choice_add_remove_phone_email(choice):

    if 'add' in choice:
        text_1 = 'добавить'
    if 'phone_num' in choice:
        text_2 = 'номер телефона'
    if 'email_address' in choice:
        text_2 = 'email'
    if 'remove' in choice:
        text_1 = 'удалить'

    print()
    print(f'Введите данные клиента, для которого нужно {text_1} {text_2}')
    print(80 * '-')
    client_info = input_client_info()
    print('\nПо введенным данным найден(ы) клиент(ы): ')
    print_table(find_client(conn, *client_info))
    print(f'\nЧтобы {text_1} {text_2}, введите ID выбранного клиента и {text_2}:')
    person_id = input('Введите ID клиента: ')

    if person_id is None or person_id == '' or not person_id.isdigit():
        print('Необходимо ввести ID клиента')
        return
    elif not find_client(conn,  '', '', '', '', '', '', int(person_id)):
        print('Такого клиента в базе данных нет')
        return
    else:
        person_id = int(person_id)

    phone_num_email = input(f'Введите {text_2}: ')

    if 'phone_num' in choice and 'add' in choice:
        insert_phone_num_for_existing_client(conn, phone_num_email, person_id)

    if 'email_address' in choice and 'add' in choice:
        insert_email_for_existing_client(conn, phone_num_email, person_id)

    if 'phone_num' in choice and 'remove' in choice:
        delete_phone_number(conn, person_id, phone_num_email)

    if 'email_address' in choice and 'remove' in choice:
        delete_email_address(conn, person_id, phone_num_email)

    if 'add' in choice:
        print(f'\nДобавлен {text_2}:')
        print_table(find_client(conn, '', '', '', '', '', '', person_id))

    if 'remove' in choice:
        print(f'\nПроверьте, что {text_2} удален:')
        print_table(find_client(conn, '', '', '', '', '', '', person_id))


def user_choice_update_client_info():

    print()
    print(f'Введите данные клиента, для которого нужно изменить данные')
    print(80 * '-')
    client_info = input_client_info()
    print('\nПо введенным данным найден(ы) клиент(ы): ')
    print_table(find_client(conn, *client_info))
    print('\nЧтобы изменить данные, введите ID выбранного клиента и данные для изменения')
    print('(если данные не меняются, ничего вводить не нужно)')
    print('(Изменить можно только Имя, Фамилию, Отчество и дату рождения):')

    person_id = input('Введите ID клиента: ')

    if person_id is None or person_id == '' or not person_id.isdigit():
        print('Необходимо ввести ID клиента')
        return
    elif not find_client(conn,  '', '', '', '', '', '', int(person_id)):
        print('Такого клиента в базе данных нет')
        return
    else:
        person_id = int(person_id)

    client_info_new = input_client_info()

    if client_info_new[0] or client_info_new[1] or client_info_new[2] or client_info_new[3]:
        update_client(conn, person_id, *client_info_new[0:4])
        print()
        print('Обновлена информация:')
        print_table(find_client(conn, '', '', '', '', '', '', person_id))
    else:
        print('Информация не введена, ничего обновлено не будет')


def user_choice_input():
    """
    Функция выбора действий пользователя второго уровня.
    Осуществляется выбор действия по добавлению новых или изменению существующих данных
    :return:
    """

    choice_dict = {'1': 'Добавить нового клиента', '2': 'Добавить телефон', '3': 'Добавить email',
                   '4': 'Изменить данные клиента', '5': 'Добавить тестовые данные'}
    choice_dict_commands = {'1': user_choice_add_new_client, '2': user_choice_add_remove_phone_email,
                            '3': user_choice_add_remove_phone_email, '4': user_choice_update_client_info,
                            '5': insert_init_data}

    print('Вы можете:')
    for k, v in choice_dict.items():
        print(k, '-', v)
    user_choice = input('Введите номер нужной функции и нажмите ввод: ')

    if user_choice in choice_dict_commands:
        if user_choice == '2':
            choice_dict_commands[user_choice](('add', 'phone_num'))
        elif user_choice == '3':
            choice_dict_commands[user_choice](('add', 'email_address'))
        else:
            choice_dict_commands[user_choice]()
    else:
        print('Такой функции нет')


def user_choice_remove_client():
    """
    Функция удаления клиента
    :return:
    """

    print()
    print(f'Введите данные клиента, которого нужно удалить')
    print(80 * '-')
    client_info = input_client_info()
    print('\nПо введенным данным найден(ы) клиент(ы): ')
    print_table(find_client(conn, *client_info))
    person_id = input('Введите ID клиента, которого хотите удалить: ')

    if person_id is None or person_id == '' or not person_id.isdigit():
        print('Необходимо ввести ID клиента')
        return
    elif not find_client(conn,  '', '', '', '', '', '', int(person_id)):
        print('Такого клиента в базе данных нет')
        return
    else:
        person_id = int(person_id)

    delete_client(conn, person_id)

    print(f'\nПроверьте, что клиент удален:')
    print_table(find_client(conn, *client_info))


def user_choice_remove_all_clients():
    """
    Функция удаления всех клиентов
    :return:
    """

    print()
    print('В базе данных находятся записи о следующих клиентах:')
    all_clients = find_client(conn, '', '', '', None, '', '')
    print_table(all_clients)
    r_u_s = input("Если вы уверены, что хотите удалить всех клиентов, введите 'да': ")

    if r_u_s == 'да':
        counter = 0
        for client in all_clients:
            delete_client(conn, client[0])
            counter += 1
    else:
        print('Ничего не будет удалено')
        return

    print('Удалено', counter, 'записей')
    print('\nСейчас в базе данных содержатся следующие записи:')
    print_table(find_client(conn, '', '', '', None, '', ''))


def user_choice_remove():
    """
    Функция выбора действий пользователя второго уровня.
    Осуществляется выбор действия по удалению данных
    :return:
    """

    choice_dict = {'1': 'Удалить телефон клиента', '2': 'Удалить email клиента', '3': 'Удалить клиента',
                   '4': 'Удалить всех клиентов'}
    choice_dict_commands = {'1': user_choice_add_remove_phone_email, '2': user_choice_add_remove_phone_email,
                            '3': user_choice_remove_client, '4': user_choice_remove_all_clients}

    print('Вы можете:')
    for k, v in choice_dict.items():
        print(k, '-', v)
    user_choice = input('Введите номер нужной функции и нажмите ввод: ')

    if user_choice in choice_dict_commands:
        if user_choice == '1':
            choice_dict_commands[user_choice](('remove', 'phone_num'))
        elif user_choice == '2':
            choice_dict_commands[user_choice](('remove', 'email_address'))
        else:
            choice_dict_commands[user_choice]()
    else:
        print('Такой функции нет')


def base_user_module():
    """
    Основной модуль, в котором пользователь выбирает действие, которое он хочет выполнить,
    а модуль вызывает соответствующую функцию
    :return: Пока непонятно, должен ли он что-то возвращать
    """

    choice_dict = {'1': 'Найти клиента', '2': 'Ввести данные', '3': 'Удалить данные', '4': 'Выйти'}
    choice_dict_commands = {'1': user_choice_find, '2': user_choice_input, '3': user_choice_remove, '4': print}

    user_choice = 0

    while user_choice != '4':
        print('\nПрограмма может выполнить следующие функции:')
        for k, v in choice_dict.items():
            print(k, '-', v)
        user_choice = input('Введите номер нужной функции и нажмите ввод: ')

        if user_choice in choice_dict_commands:
            choice_dict_commands[user_choice]()
        else:
            print('Такой функции нет')


if __name__ == '__main__':

    conn = psycopg2.connect(database="", user="", password="")

    create_tables(conn)

    base_user_module()

    conn.close()
