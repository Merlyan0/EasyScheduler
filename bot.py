import json
from datetime import datetime
from pprint import pprint

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from db import add_to_db, create_connection

token = 'ваш_токен'
group_id = 'id_сообщества_вк'

# подключение к сервисам API ВКонтакте
vk_session = vk_api.VkApi(token = token)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id)

# подключение к базе данных
__temp = create_connection()
db_conn = __temp[0]
db_cur = __temp[1]


def main_menu():
    """
    Функция для отрисовки главного меню бота.
    """
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('&#128195; Список напоминаний')

    keyboard.add_line()
    keyboard.add_button('&#128221; Создать напоминание', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('&#9989; Завершить напоминание', color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()
    keyboard.add_button('&#9881; Настройки', color=VkKeyboardColor.PRIMARY)

    vk.messages.send(peer_id=event.object.message["peer_id"],
                     message="Главное меню",
                     random_id=get_random_id(),
                     keyboard=keyboard.get_keyboard())


def settings():
    """
    Функция для отрисовки настроек бота.
    """
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('&#128281; Главное меню')

    vk.messages.send(peer_id=event.object.message["peer_id"],
                     message="Скоро тут появятся настройки",
                     random_id=get_random_id(),
                     keyboard=keyboard.get_keyboard())


def create_reminder():
    """
    Функция для создания напоминания в боте.
    """
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('&#128281; Главное меню')

    vk.messages.send(peer_id=event.object.message["peer_id"],
                     message="Хорошо. Введите название напоминания.",
                     random_id=get_random_id(),
                     keyboard=keyboard.get_keyboard())


for event in longpoll.listen():

    # пришло новое сообщение
    if event.type == VkBotEventType.MESSAGE_NEW:
        pprint(event.object)

        message = event.object.message["text"].lower()  # присланное сообщение

        if message == 'главная' or message == '🔙 главное меню':
            main_menu()

        elif message == '⚙ настройки' or message == 'настройки':
            settings()

        elif message == '📝 создать напоминание' or message == 'создать напоминание' or message == 'создать':
            create_reminder()
