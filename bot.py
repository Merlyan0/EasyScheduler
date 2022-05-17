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


def every_minute() -> None:
    """
    Выполнение различных действий каждую минуту.
    """
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
        peer_id = event.object.message["peer_id"]  # id диалога в боте

        # команда главного меню
        if message == 'главная' or message == '🔙 главное меню':
            handler.main_menu(peer_id)

        # команда настроек
        elif message == '⚙ настройки' or message == 'настройки':
            handler.settings(peer_id)

        # команда перехода в ручное меню
        elif message == '📝 ручной режим' or message == 'ручной режим' or message == 'ручной':
            handler.manual_mode(peer_id)

        # команда ручного создания напоминаний
        elif message == '📝 создать напоминание' or message == 'создать напоминание' or message == 'создать':
            handler.create_manually_step1(peer_id)

        # команда просмотра расписания
        elif message == '📃 список напоминаний' or message == 'список' or message == 'расписание':
            handler.timetable(peer_id, datetime.now())

        # команда завершения напоминания
        elif message == '✅ завершить напоминание' or message == 'завершить' or message == 'завершить напоминание':
            handler.finish_step1(peer_id)

        # команда начать: приветствие пользователя
        elif message == 'начать':
            handler.start(peer_id)

        else:

            try:
                # id предыдущего сообщение
                conv_mess_id = event.object.message["conversation_message_id"] - 1

                # предыдущее сообщение
                prev_mess = vk.messages.getByConversationMessageId(peer_id=peer_id,
                                                                   conversation_message_ids=conv_mess_id)
                prev_mess = prev_mess['items'][0]['text']

            except (BaseException,):
                prev_mess = ''

            if prev_mess == handler.get_message("MESS_HOW_TO_REMOVE"):
                handler.finish_step2(event)

            elif prev_mess == handler.get_message("MESS_CREATE_REMINDER"):
                handler.create_manually_step2(event)

            elif prev_mess == handler.get_message("MESS_CREATE_REMINDER_COMPLETED_1"):
                handler.create_manually_step3(event)

            else:
                handler.reminder_analyzer(event)

    elif event.type == VkBotEventType.MESSAGE_EVENT:

        if event.object.payload.get("type") == "set_finish":
            handler.set_finished(event.object, event.object.payload.get("id"))

        elif event.object.payload.get("type") == "set_delayed":
            handler.set_delayed(event.object, event.object.payload.get("id"))
