import mysql.connector
from mysql.connector import Error
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

class MySQLManager:
    def __init__(self):
        self.connection = None

    def connect(self):
        """Устанавливает соединение с MySQL"""
        try:
            self.connection = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE
            )
            if self.connection.is_connected():
                print("Connected to MySQL")
        except Error as e:
            print(f"Ошибка подключения к MySQL: {e}")
            raise

    def create_table(self):
        """Создаёт таблицу weather_data, если её нет"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS weather_data (
            datetime DATETIME PRIMARY KEY,
            temperature DOUBLE,
            pressure DOUBLE,
            humidity DOUBLE,
            pm25 DOUBLE,
            pm10 DOUBLE,
            co DOUBLE,
            no2 DOUBLE,
            so2 DOUBLE,
            o3 DOUBLE,
            h2s DOUBLE,
            aqi DOUBLE
        )
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_query)
            self.connection.commit()
            print("Таблица weather_data создана или уже существует")
        except Error as e:
            print(f"Ошибка создания таблицы: {e}")

    def insert_measurement(self, data: dict):
        """Добавляет одну запись в БД"""
        insert_query = """
        INSERT INTO weather_data (
            datetime, temperature, pressure, humidity, pm25, pm10,
            co, no2, so2, o3, h2s, aqi
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""