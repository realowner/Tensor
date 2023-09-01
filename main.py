from utils.dbmanager import DBManager
from utils.funcs import get_data
from termcolor import cprint  # для разнообразия вывода


def main() -> None:
    """
    Функция основной логики
    :return: None
    """
    db_client = DBManager()

    while True:
        user_choice = input('Выберите один из вариантов:\n'
                            '1 - создать базу данных и заполнить ее\n'
                            '2 - перейти к запросу (если первый шаг был выполнен ранее)\n'
                            '3 - выход\n'
                            '--> ')

        if user_choice == '1':
            # Проверяю создана ли БД в текущей сессии
            if db_client.created:
                cprint('БД и таблицы уже созданы в этой сессии', 'green')
                continue

            office_data, department_data, employee_data = get_data()
            db_client.create_db()
            db_client.insert_data(office_data, department_data, employee_data)

            cprint('БД создана и заполнена', 'green')

        elif user_choice == '2':
            # Если БД не создана в этой сессии
            if not db_client.created:
                cprint('БД не создана в этой сессии, выполните шаг 1', 'green')
                continue
            # Если соединение не установлено, создаем его
            if not db_client.connection:
                db_client.make_conn()
                cprint('Соединение с БД установлено', 'green')

            employee_id = input('Введите id работника:\n--> ')
            # Если ввели не число
            if not employee_id.isdigit():
                cprint('Недопустимый ввод', 'green')
                continue
            response = db_client.query(employee_id)

            cprint('=' * 10)
            if len(response) != 0:
                for name_item in response:
                    cprint(name_item[0], 'green')
            else:
                cprint('Нет результата', 'green')
            cprint('=' * 10)

        elif user_choice == '3':
            # Если соединение установлено, закрываем его его
            if db_client.connection:
                db_client.close_conn()
                cprint('Соединение с БД закрыто', 'green')

            quit('Завершено')


if __name__ == '__main__':
    main()
