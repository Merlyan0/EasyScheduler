# прочее
from datetime import datetime
from pprint import pprint

# VK API
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

# парсер даты
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from DateParser_ru.parser import analyze_string

# работа с базой данных
from data.scripts.db import create_connection, add_to_db, set_date

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
handler = BotHandler(vk)

# все приходящие с сервера события
for event in longpoll.listen():

    # пришло новое сообщение
    if event.type == VkBotEventType.MESSAGE_NEW:
        pprint(event.object)

        message = event.object.message["text"].lower()  # присланное сообщение

        if message == 'главная' or message == '🔙 главное меню':
            print(handler.get_message("MESS_CREATE_REMINDER"))
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

            if prev_mess['items'][0]['text'] == handler.get_message('MESS_CREATE_REMINDER'):
                add_to_db(db_conn, db_cur, title=event.object.message["text"], author=event.object.message["from_id"],
                          finished=False, created_date=datetime.now())

                vk.messages.send(peer_id=event.object.message["peer_id"],
                                 message=handler.get_message('MESS_CREATE_REMINDER_COMPLETED_1'),
                                 random_id=get_random_id())

            elif prev_mess['items'][0]['text'] == handler.get_message('MESS_CREATE_REMINDER_COMPLETED_1'):
                date = event.object.message["text"]
                if len(date.split()[0].split('.')) == 3:
                    a = datetime(year=int(date.split()[0].split('.')[2]), month=int(date.split()[0].split('.')[1]),
                                 day=int(date.split()[0].split('.')[1]))
                elif len(date.split()[0].split('.')) == 2:
                    a = datetime(year=datetime.now().year, month=int(date.split()[0].split('.')[1]),
                                 day=int(date.split()[0].split('.')[0]))
                else:
                    a = datetime(year=datetime.now().year, month=datetime.now().month,
                                 day=int(date.split()[0].split('.')[0]))

                a = a.replace(hour=int(date.split()[1].split(":")[0]), minute=int(date.split()[1].split(":")[1]))

                set_date(db_conn, db_cur, event.object.message['from_id'], a.strftime('%d/%m/%Y %H:%M'))

            else:
                a = analyze_string(message)
                if a[0] == 'Ошибка':
                    vk.messages.send(peer_id=event.object.message["peer_id"],
                                     message=f"&#10060; {a[0]} \n\n"
                                             f"{a[1]}",
                                     random_id=get_random_id())

                elif a[2]['date'] is False and a[2]['time'] is False:
                    title = ' '.join(a[1]).capitalize()
                    keyboard = VkKeyboard(one_time=False, inline=True)
                    keyboard.add_callback_button(
                        label="Подтвердить",
                        color=VkKeyboardColor.POSITIVE,
                        payload={"type": "confirm", "title": f"{title}",
                                 "time": f"{a[0].strftime('%d.%m.%Y в %H:%M')}"},
                    )
                    vk.messages.send(peer_id=event.object.message["peer_id"],
                                     message=f"&#9989; Напоминание создано! \n\n"
                                             f"-> {title} \n"
                                             f"-> Даты в сообщении не обнаружено. \n\n"
                                             f"Если всё так, нажмите кнопку \"Подтвердить\"",
                                     random_id=get_random_id(),
                                     keyboard=keyboard.get_keyboard())
                else:
                    title = ' '.join(a[1]).capitalize()
                    keyboard = VkKeyboard(one_time=False, inline=True)
                    keyboard.add_callback_button(
                        label="Подтвердить",
                        color=VkKeyboardColor.POSITIVE,
                        payload={"type": "confirm", "title": f"{title}",
                                 "time": f"{a[0].strftime('%d.%m.%Y в %H:%M')}"},
                    )

                    vk.messages.send(peer_id=event.object.message["peer_id"],
                                     message=f"&#10068; Напоминание определено. \n\n"
                                             f"-> {title} \n"
                                             f"-> Дата: {a[0].strftime('%d.%m.%Y в %H:%M')}. \n\n"
                                             f"Если всё так, нажмите кнопку \"Подтвердить\"",
                                     random_id=get_random_id(),
                                     keyboard=keyboard.get_keyboard())

    elif event.type == VkBotEventType.MESSAGE_EVENT:

        print(event.object)

        if event.object.payload.get("type") == "confirm":
            handler.confirm_info(event)
