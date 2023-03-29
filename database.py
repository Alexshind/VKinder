import psycopg2


class DataBase:
    '''This class is intended for connecting to a Database and adding new data to tables'''

    def __init__(self):
        self.conn = None

    def bd_connect(self, db_name, db_user, db_password, db_host, db_port):
        '''Function for connecting to the database'''

        try:
            self.conn = psycopg2.connect(
                database=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            print('Успешное подключение к базе данных')
        except:
            print(input('Ошибка подключения к базе данных.\nПроверьте, верно ли ввели данные в файле token_bd.ini\nНажмите на Enter...'))
            exit()

    def create_table(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_people (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                person_id INTEGER REFERENCES people(id)
            );
        """)
        self.conn.commit()
        cursor.close()

    def add_user_to_table(self, user_id):
        if user_id:
            cursor = self.conn.cursor()
            if not self.check_user_id_in_table(user_id):
                cursor.execute(
                    f'''INSERT INTO users (id) VALUES ({user_id})''')
                self.conn.commit()
            cursor.close()

    def check_user_id_in_table(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f'SELECT EXISTS(SELECT 1 FROM users WHERE id = {user_id})')
        exists = cursor.fetchone()[0]
        cursor.close()
        return exists

    def add_people_to_table(self, user_id):
        if user_id:
            cursor = self.conn.cursor()
            if not self.check_people_id_in_table(user_id):
                cursor.execute(
                    f'''INSERT INTO people (id) VALUES ({user_id})''')
                self.conn.commit()
            cursor.close()

    def check_people_id_in_table(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f'SELECT EXISTS(SELECT 1 FROM people WHERE id = {user_id})')
        exists = cursor.fetchone()[0]
        cursor.close()
        return exists

    def add_person_to_user(self, user_id, person_id):
        '''This function adds a person_id to the user_id in the user_people table'''

        cursor = self.conn.cursor()

        if self.check_user_id_in_table(user_id) and self.check_people_id_in_table(person_id):
            cursor.execute(
                'SELECT id FROM user_people WHERE user_id = %s AND person_id = %s', (user_id, person_id))
            up_data = cursor.fetchone()
            if up_data is not None:
                return

            cursor.execute(
                'INSERT INTO user_people (user_id, person_id) VALUES (%s, %s)', (user_id, person_id))

            self.conn.commit()
            cursor.close()

    def get_linked_users(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT person_id FROM user_people WHERE user_id = %s", (user_id,))
        result = cursor.fetchall()
        cursor.close()
        linked_users = [r[0] for r in result]
        return linked_users
