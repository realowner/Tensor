import psycopg2
from dotenv import load_dotenv  # переменные окружения
import os

load_dotenv()


class DBManager:
    """
    Класс менеджер для работы с БД
    """

    def __init__(self):
        self.__conn = None  # атрибут для соединения
        self.__db_name = 'tensor_test'  # имя бд для создания
        self.__already_created = False  # создана БД или нет

    @property
    def connection(self) -> object:
        """
        Геттер для __conn
        :return: connection object
        """
        return self.__conn

    @property
    def created(self) -> bool:
        """
        Геттер для __conn
        :return: bool
        """
        return self.__already_created

    def make_conn(self) -> None:
        """
        Метод соединения с БД
        :return: None
        """
        conn = psycopg2.connect(dbname=self.__db_name, user=os.getenv('USER'), password=os.getenv('PASSWORD'))
        conn.autocommit = True
        self.__conn = conn

    def close_conn(self) -> None:
        """
        Метод закрытия соединения с БД
        :return: None
        """
        self.__conn.close()

    def create_db(self) -> None:
        """
        Метод первоначального создания БД. Удаляет если существует и создает новую.
        После чего вызывает метод для установки связи с новой БД и метод создания таблиц в ней.
        :return: None
        """
        conn = psycopg2.connect(dbname="postgres", user=os.getenv('USER'), password=os.getenv('PASSWORD'))
        conn.autocommit = True

        with conn.cursor() as cur:
            cur.execute(f"""DROP DATABASE IF EXISTS {self.__db_name};""")
            cur.execute(f"""CREATE DATABASE {self.__db_name};""")

        conn.close()
        self.make_conn()
        self.create_tables()

    def create_tables(self) -> None:
        """
        Метод создания таблиц в новой БД
        :return: None
        """
        with self.__conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE office (
                    id INT PRIMARY KEY,
                    name VARCHAR(100),
                    type INT
                );
            """)

            cur.execute("""
                CREATE TABLE department (
                    id INT PRIMARY KEY,
                    office_id INT REFERENCES office(id),
                    name VARCHAR(255),
                    type INT
                );
            """)

            cur.execute("""
                CREATE TABLE employee (
                    id INT PRIMARY KEY,
                    department_id INT REFERENCES department(id),
                    name VARCHAR(50),
                    type INT
                );
            """)

        self.__conn.commit()
        self.__already_created = True

    def insert_data(self, off_data: list, dep_data: list, emp_data: list) -> None:
        """
        Метод для заполнения таблиц данными
        :param off_data: список офисов
        :param dep_data: список отделов
        :param emp_data: список работников
        :return: None
        """
        with self.__conn.cursor() as cur:
            for item in off_data:
                cur.execute("""
                    INSERT INTO office (id, name, type) VALUES (%s, %s, %s);""", (
                    item.get('id'),
                    item.get('Name'),
                    item.get('Type')
                ))

            for item in dep_data:
                cur.execute("""
                    INSERT INTO department (id, office_id, name, type) VALUES (%s, %s, %s, %s);""", (
                    item.get('id'),
                    item.get('ParentId'),
                    item.get('Name'),
                    item.get('Type')
                ))

            for item in emp_data:
                cur.execute("""
                    INSERT INTO employee (id, department_id, name, type) VALUES (%s, %s, %s, %s);""", (
                    item.get('id'),
                    item.get('ParentId'),
                    item.get('Name'),
                    item.get('Type')
                ))

    def query(self, emp_id: str) -> list:
        """
        Основной запрос ТЗ
        :param emp_id: id работника
        :return: list
        """
        with self.__conn.cursor() as cur:
            # Решил с помощью вложенных циклов.
            # Достаю отдел по id работника, офис по id отдела,
            # после чего достаю всех работников определенного офиса
            #
            # Вероятно, не оптимальное решение,
            # но моих знаний сырых запросов хватает на такой вариант)
            cur.execute(f"""
                SELECT e.name FROM office AS o
                JOIN department AS d ON o.id = d.office_id
                JOIN employee AS e ON d.id = e.department_id
                WHERE o.id = (SELECT office_id 
                              FROM department
                              WHERE id = (SELECT department_id 
                                          FROM employee 
                                          WHERE id = {emp_id}));
            """)

            return cur.fetchall()
