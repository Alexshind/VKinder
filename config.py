from os import listdir


class ReadConfig:
    '''This class read token.ini file and return tokens'''

    def __init__(self):
        self.__token_group = None
        self.__token_user = None

        self.__db_name_connect = None
        self.__db_password = None
        self.__db_name = None
        self.__db_host = None
        self.__db_port = None

    def check_config(self):
        if not 'token_bd.ini' in listdir():
            with open('token_bd.ini', 'w', encoding='UTF-8') as f:
                f.write('''Введите токен группы и токен пользователя.

Token group:
Token user:

Если ваши данные к подключению к СУБД отличаются, то измените следующие параметры:

db_name: vkinder
db_user: postgres
db_password: 1234
db_host: localhost
db_port: 5432''')

        return True

    def get_tokens(self):
        '''This func get tokens'''
        if self.check_config():
            with open('token_bd.ini', 'r', encoding='UTF-8') as f:
                self.__token_group, self.__token_user = [line.replace(
                    '\n', '').split() for line in f if 'Token' in line]

            if self.__token_group[-1][:3] != 'vk1' or self.__token_user[-1][:3] != 'vk1':
                print(input(
                    'Вы ввели не все данные в файле token_bd.ini\nНажмите на Enter...'))
                exit()

            return self.__token_group[-1], self.__token_user[-1]

    def get_bd(self):
        '''This func get bd'''
        if self.check_config():
            with open('token_bd.ini', 'r', encoding='UTF-8') as f:
                self.__db_name_connect, self.__db_password, self.__db_name, self.__db_host, self.__db_port = [
                    line.replace('\n', '').split() for line in f if 'db' in line]

            return self.__db_name_connect[-1], self.__db_password[-1], self.__db_name[-1], self.__db_host[-1], self.__db_port[-1]
