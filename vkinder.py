from random import choice

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

from config import ReadConfig
from database import DataBase

token_session, token_access = ReadConfig().get_tokens()
dbname, user, password, host, port = ReadConfig().get_bd()

database = DataBase()
database.bd_connect(dbname, user, password, host, port)
database.create_table()

vk_session = vk_api.VkApi(token=token_session, api_version='5.131')
vk_access = vk_api.VkApi(token=token_access, api_version='5.131').get_api()
longpoll = VkLongPoll(vk_session)


class BotFunc():
    '''This class is intended for button calls'''
    @staticmethod
    def write_msg(user_id, message, keyboard=None, attachment=None):
        __base_requset = {'user_id': user_id,
                          'message': message,
                          'random_id': 0
                          }

        if keyboard != None:
            __base_requset['keyboard'] = keyboard.get_keyboard()

        if attachment != None:
            __base_requset['attachment'] = ','.join(attachment)

        vk_session.method('messages.send', __base_requset)

    @staticmethod
    def start_button():
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Начать поиск!', VkKeyboardColor.POSITIVE)
        return keyboard

    @staticmethod
    def search_buttons():
        return {'Следующий': VkKeyboardColor.POSITIVE,
                'Закончить': VkKeyboardColor.NEGATIVE}

    def get_random(self, user_id: str, random_user_list: list, start_or_next=False):
        keyboard = None

        if random_user_list != False:
            random_user = People.get_random_cache_user(user_id)

            if start_or_next:
                keyboard = VkKeyboard()
                for k, v in self.search_buttons().items():
                    keyboard.add_button(k, v)

            self.write_msg(
                user_id, f'{api_func.get_user_info(random_user)["first_name"]}\nhttps://vk.com/id{random_user}', keyboard, api_func.get_top_photos(random_user))

        else:
            self.write_msg(
                user_id, 'Приносим наши извинения! На сервере VK произошли сбои. Попробуйте попытку позже!', self.start_button())


class BotApiFunc:
    '''This class works with the VK API'''

    @staticmethod
    def get_user_info(user_id):
        '''The function returns all information about the user'''

        user_info = vk_access.users.get(
            user_ids=user_id, fields='first_name,last_name,sex,bdate,city,country,relation,counters')
        return {'id': user_info[0]['id'],
                'first_name': user_info[0]['first_name'],
                'last_name': user_info[0]['last_name'],
                'sex': user_info[0]['sex'],
                'bdate': user_info[0]['bdate'],
                'city': user_info[0]['city']['title'] if 'city' in user_info[0] else None,
                'country': user_info[0]['country']['title'] if 'country' in user_info[0] else None,
                'relation': user_info[0]['relation'] if 'relation' in user_info[0] else None,
                }

    @classmethod
    def checking(cls, id):
        '''This function is designed to verify all user data'''
        return 'bdate' in cls.get_user_info(id) and 'sex' in cls.get_user_info(id) and cls.get_user_info(id)['city'] != None

    @classmethod
    def get_random_user(cls, city, user_sex, user_bdate):
        '''The function returns a list of people matching the user's criteria'''

        city_id = vk_access.database.getCities(country_id=1, q=city)['items'][0]['id']
        result = vk_access.users.search(q='', 
                                        city=city_id, 
                                        sex=3 - user_sex, 
                                        status=6, 
                                        fields='bdate', 
                                        count=1000
                                        )
        try:
            result = [user['id'] for user in result['items'] if ('bdate' in user and 
                                                                 user['bdate'].count('.') == 2 and 
                                                                 abs(int(user['bdate'].split('.')[-1]) - int(user_bdate.split('.')[-1])) <= 5 and 
                                                                 user['is_closed'] == False)]
            return result
        except KeyError:
            return False

    @ classmethod
    def get_top_photos(cls, user_id):
        '''The function returns the most popular photos of the user by likes and comments'''

        photos = vk_access.photos.get(owner_id=user_id,
                                      album_id='profile',
                                      extended=1,
                                      count=200
                                      )

        photos = sorted(photos['items'], key=lambda x: x['likes']
                        ['count'] + x['comments']['count'], reverse=True)[:3]
        try:
            result = [f"photo{p['owner_id']}_{p['id']}" for p in photos]
            return result
        except KeyError:
            return None


class People:
    '''This class keep user id in cache memory'''
    __instance_people_list = dict()

    def __new__(cls, **kwargs):
        for key, value in kwargs.items():
            if (key not in cls.__instance_people_list and
                    not database.check_user_id_in_table(key)):
                cls.__instance_people_list[key] = value

            elif (key not in cls.__instance_people_list and
                  database.check_user_id_in_table(key)):
                cls.__instance_people_list[key] = [i for i in value if i not in database.get_linked_users(key)]
            else:
                pass

    @classmethod
    def show_people_list(cls):
        return cls.__instance_people_list

    @classmethod
    def get_random_cache_user(cls, user_id):
        user_id = str(user_id)
        if user_id in cls.__instance_people_list:
            random_cache_user = choice(cls.__instance_people_list[user_id])
            cls.__instance_people_list[user_id].remove(random_cache_user)
            database.add_people_to_table(random_cache_user)
            database.add_person_to_user(user_id, random_cache_user)
            return random_cache_user


not_api_func = BotFunc()
api_func = BotApiFunc()


class VKinder():
    '''This class is designed to run a bot'''
    @classmethod
    def start_bot(cls):
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                user_id = event.user_id

                match event.text.lower():

                    case 'начать':
                        database.add_user_to_table(user_id)
                        not_api_func.write_msg(
                            user_id, f"Йо! {api_func.get_user_info(user_id)['first_name']}. Для поиска пары нажми на 'Начать поиск!'", not_api_func.start_button())

                    case 'начать поиск!':
                        if api_func.checking(user_id):
                            if (str(user_id) in People.show_people_list() and
                                    People.show_people_list()[str(user_id)]):
                                not_api_func.get_random(
                                    user_id, random_user_list, True)
                            else:
                                random_user_list = api_func.get_random_user(api_func.get_user_info(user_id)['city'],
                                                                            api_func.get_user_info(user_id)['sex'],
                                                                            api_func.get_user_info(user_id)['bdate']
                                                                            )
                                People(**{str(user_id): random_user_list})
                                not_api_func.get_random(user_id, random_user_list, True)
                        else:
                            not_api_func.write_msg(
                                user_id, 'Проверьте, на вашем профиле должны быть указаны такие параметры:\n-Ваш возраст\n-Ваш пол\n-Ваш город')

                    case 'следующий':
                        if api_func.checking(user_id):
                            if (str(user_id) in People.show_people_list() and
                                    People.show_people_list()[str(user_id)]):
                                not_api_func.get_random(user_id, random_user_list)
                            else:
                                random_user_list = api_func.get_random_user(api_func.get_user_info(user_id)['city'],
                                                                            api_func.get_user_info(user_id)['sex'],
                                                                            api_func.get_user_info(user_id)['bdate']
                                                                            )
                                People(**{str(user_id): random_user_list})
                                not_api_func.get_random(user_id, random_user_list)
                        else:
                            not_api_func.write_msg(
                                user_id, 'Проверьте, на вашем профиле должны быть указаны такие параметры:\n-Ваш возраст\n-Ваш пол\n-Ваш город')

                    case 'закончить':
                        not_api_func.write_msg(
                            user_id, 'Успехов!', not_api_func.start_button())

                    case _:
                        not_api_func.write_msg(
                            user_id, 'Я не знаю таких команд!', not_api_func.start_button())
