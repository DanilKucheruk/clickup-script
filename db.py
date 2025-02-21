import pymysql

# Данные для подключения к базе данных Битрикс24
DB_HOST = 'your-db-host'      # IP или адрес сервера БД
DB_USER = 'your-db-user'      # Логин
DB_PASSWORD = 'your-db-pass'  # Пароль
DB_NAME = 'your-db-name'      # Название базы данных

def get_tasks_by_group(group_id):
    try:
        # Подключение к БД
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor  # Результаты в виде словаря
        )

        with connection.cursor() as cursor:
            sql = "SELECT ID, TITLE, RESPONSIBLE_ID FROM b_tasks WHERE GROUP_ID = %s"
            cursor.execute(sql, (group_id,))  # Передаём group_id безопасно через параметры
            tasks = cursor.fetchall()  # Получаем все задачи

        return tasks

    except pymysql.MySQLError as e:
        print(f"Ошибка подключения к БД: {e}")
        return []

    finally:
        if connection:
            connection.close()  # Закрываем соединение

if __name__ == "__main__":
    group_id = 12345  # ID нужной группы
    tasks = get_tasks_by_group(group_id)
    
    for task in tasks:
        print(f"Задача ID: {task['ID']}, Название: {task['TITLE']}, Ответственный: {task['RESPONSIBLE_ID']}")
