# прочее
import threading
import time
from datetime import datetime
from pprint import pprint

# VK API
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# работа с базой данных
from data.scripts.db import DataBase

# обработчик команд
from data.scripts.handler import BotHandler

# настройки из конфига
from config import *


# подключение к сервисам API ВКонтакте
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

# подключение к базе данных
db = DataBase()

# экземляр обработчика команд
handler = BotHandler(vk, db)


def every_minute():
    while datetime.now().second != 0:
        time.sleep(1)

    threading.Timer(60.0, every_minute).start()

    handler.send_reminders(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


# отправка подошедших по времени напоминаний
every_minute()


# все приходящие с сервера события
for event in longpoll.listen():

    # пришло новое сообщение
    if event.type == VkBotEventType.MESSAGE_NEW:
        pprint(event.object)

        message = event.object.message["text"].lower()  # присланное сообщение

        # команда главного меню
        if message == 'главная' or message == '🔙 главное меню':
            handler.main_menu(event.object.message["peer_id"])

        elif message == '⚙ настройки' or message == 'настройки':
            handler.settings(event.object.message["peer_id"])

        elif message == '📝 создать напоминание' or message == 'создать напоминание' or message == 'создать':
            handler.create_reminder(event.object.message["peer_id"])

        elif message == 'начать':
            handler.start(event.object.message["peer_id"])

        else:
            # id предыдущего сообщение
            conv_mess_id = event.object.message["conversation_message_id"] - 1
            # предыдущее сообщение
            prev_mess = vk.messages.getByConversationMessageId(peer_id=event.object.message["peer_id"],
                                                               conversation_message_ids=conv_mess_id)

            if prev_mess['items'][0]['text'] == handler.get_message("MESS_CREATE_REMINDER"):
                handler.create_manually(event)

            elif prev_mess['items'][0]['text'] == handler.get_message("MESS_CREATE_REMINDER_COMPLETED_1"):
                handler.create_manually_step2(event)

            else:
                handler.reminder_analyzer(event)

    elif event.type == VkBotEventType.MESSAGE_EVENT:

        print(event.object)

        if event.object.payload.get("type") == "confirm":
            handler.confirm_info(event)
