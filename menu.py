from keyboards import KEYBOARD_start, KEYBOARD_main, KEYBOARD_yes_or_no, KEYBOARD_favorites


class Command:
    START = 'Старт'
    NEXT_PERSON = 'Далее'
    STOP = 'Стоп'
    ADD_TO_FAVORITE = 'Добавить в избранное'
    OPEN_FAVORITE = 'Открыть избранное'
    DELETE = 'Удалить'
    OPEN_MAIN_MENU = 'Главное меню'
    YES = 'Да'
    NO = 'Нет'


class Position:
    INTRO = 0
    IN_MAIN_MENU = 1
    IN_ADD_FAVORITE_MENU = 2
    IN_FAVORITE_MENU = 3
    IN_DELETE_FAVORITE_MENU = 4
    NEED_AGE = 404
    NEED_CITY = 405

    KEYBOARDS = {INTRO: KEYBOARD_start,
                 IN_MAIN_MENU: KEYBOARD_main,
                 IN_ADD_FAVORITE_MENU: KEYBOARD_yes_or_no,
                 IN_FAVORITE_MENU: KEYBOARD_favorites,
                 IN_DELETE_FAVORITE_MENU: '',
                 NEED_AGE: '',
                 NEED_CITY: ''}

    @classmethod
    def get_keyboard_from_position(self, position):
        return self.KEYBOARDS[position]
