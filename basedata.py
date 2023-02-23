from random import choice
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

    def save_user_with_people_list(self, user, people_list):
        '''This function saves the new user to the Database and binds the list of people to our new user'''

        user_id, first_name, last_name, sex, bdate, city, country, relation = user.values()
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id bigint PRIMARY KEY,
                first_name text,
                last_name text,
                sex text,
                bdate text,
                city text,
                country text,
                relation text
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS people (
                id bigint PRIMARY KEY,
                first_name text,
                last_name text,
                bdate text,
                can_access_closed boolean,
                is_closed boolean
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_people (
                id SERIAL PRIMARY KEY,
                user_id bigint REFERENCES users(id),
                person_id bigint REFERENCES people(id)
            );
        """)

        cursor.execute('SELECT id FROM users WHERE id = %s', (user_id,))
        user_data = cursor.fetchone()
        if user_data is None:
            cursor.execute(
                'INSERT INTO users (id, first_name, last_name, sex, bdate, city, country, relation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                (user_id, first_name, last_name,
                 sex, bdate, city, country, relation)
            )

        for person in people_list:
            cursor.execute(
                'SELECT id FROM people WHERE id = %s', (person['id'],))
            person_data = cursor.fetchone()
            if person_data is None:
                cursor.execute(
                    'INSERT INTO people (id, first_name, last_name, bdate, can_access_closed, is_closed) VALUES (%s, %s, %s, %s, %s, %s)',
                    (person['id'], person['first_name'], person['last_name'],
                     person['bdate'], person['can_access_closed'], person['is_closed'])
                )

        for person in people_list:
            cursor.execute(
                'SELECT id FROM user_people WHERE user_id = %s AND person_id = %s', (user_id, person['id']))
            up_data = cursor.fetchone()
            if up_data is None:
                cursor.execute(
                    'INSERT INTO user_people (user_id, person_id) VALUES (%s, %s)', (user_id, person['id']))

        self.conn.commit()
        cursor.close()

    def get_random_user(self, user_id):
        '''Function for getting a random id'''

        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT person_id FROM user_people WHERE user_id = %s', (user_id,))
        all_person_ids = [person_id[0] for person_id in cursor.fetchall()]

        if len(all_person_ids) == 0:
            return None

        selected_person_id = choice(all_person_ids)
        all_person_ids.remove(selected_person_id)
        cursor.execute('DELETE FROM user_people WHERE user_id = %s AND person_id = %s',
                       (user_id, selected_person_id))

        self.conn.commit()
        return selected_person_id
