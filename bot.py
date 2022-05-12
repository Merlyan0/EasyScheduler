# прочее
from pprint import pprint

# VK API
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# работа с базой данных
from data.scripts.db import create_connection

# обработчик команд
from data.scripts.handler import BotHandler

# настройки из конфига
from config import *


# подключение к сервисам API ВКонтакте
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

# подключение к базе данных
__temp = create_connection()
db_conn = __temp[0]
db_cur = __temp[1]

# экземляр обработчика команд
handler = BotHandler(vk, db_conn, db_cur)

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
            if not handler.create_manually(event):

                handler.reminder_analyzer(event)

    elif event.type == VkBotEventType.MESSAGE_EVENT:

        print(event.object)

        if event.object.payload.get("type") == "confirm":
            handler.confirm_info(event)
