import json
from datetime import datetime

from vk_api.utils import get_random_id

from DateParser.parser import analyze_string
from data.scripts.db import add_to_db, set_date
from data.scripts.functions import check_date
from data.scripts.keyboards import *
from data.scripts.messages import *


class BotHandler:
    def __init__(self, vk, db_conn, db_cur):
        self.vk = vk
        self.db_conn = db_conn
        self.db_cur = db_cur

    def main_menu(self, peer_id):
        """
        Функция для отрисовки главного меню бота.
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=MESS_MAIN_MENU,
                              random_id=get_random_id(),
                              keyboard=KB_MAIN_MENU.get_keyboard())

    def settings(self, peer_id):
        """
        Функция для отрисовки настроек бота.
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=MESS_SETTINGS,
                              random_id=get_random_id(),
                              keyboard=KB_BACK.get_keyboard())

    def create_reminder(self, peer_id):
        """
        Функция для создания напоминания в боте.
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=MESS_CREATE_REMINDER,
                              random_id=get_random_id(),
                              keyboard=KB_BACK.get_keyboard())

    def start(self, peer_id):
        """
        Функция, приветствующая пользователя при начале общения.
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=MESS_CREATE_REMINDER,
                              random_id=get_random_id(),
                              keyboard=KB_BACK.get_keyboard())

    def confirm_info(self, event):
        title = event.object.payload.get("title")
        time = event.object.payload.get("time")

        self.vk.messages.sendMessageEventAnswer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
            event_data=json.dumps({"type": "show_snackbar", "text": "Напоминание создано."}))

        self.vk.messages.send(peer_id=event.object.peer_id,
                              message=MESS_REMINDER_CONFIRMED.substitute(title=title, time=time),
                              random_id=get_random_id())

        self.vk.messages.delete(message_ids=event.object.conversation_message_id,
                                delete_for_all=True)

    def create_manually(self, event):
        # id предыдущего сообщение
        conv_mess_id = event.object.message["conversation_message_id"] - 1
        # предыдущее сообщение
        prev_mess = self.vk.messages.getByConversationMessageId(peer_id=event.object.message["peer_id"],
                                                                conversation_message_ids=conv_mess_id)

        print(prev_mess)

        if prev_mess['items'][0]['text'] == MESS_CREATE_REMINDER:
            add_to_db(self.db_conn, self.db_cur, title=event.object.message["text"],
                      author=event.object.message["from_id"],
                      finished=False, created_date=datetime.now())

            self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                  message=MESS_CREATE_REMINDER_COMPLETED_1,
                                  random_id=get_random_id())

            return True

        elif prev_mess['items'][0]['text'] == MESS_CREATE_REMINDER_COMPLETED_1:
            date = event.object.message["text"]

            date = check_date(date)

            set_date(self.db_conn, self.db_cur, event.object.message['from_id'], date.strftime('%Y-%m-%d %H:%M:%S'))

            return True

        return False

    def reminder_analyzer(self, event):
        a = analyze_string(event.object.message["text"].lower())

        # DataParser вернул сообщение об ошибке
        if a[0] == 'Ошибка':
            self.vk.messages.send(peer_id=event.object.message["peer_id"],
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

            self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                  message=MESS_REMINDER_RECEIVED_NO_DATA.substitute(title=title),
                                  random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard())

        elif a[2]['time'] is False:
            title = ' '.join(a[1]).capitalize()
            date = a[0].strftime('%d.%m.%Y')

            keyboard = VkKeyboard(one_time=False, inline=True)
            keyboard.add_callback_button(
                label="Подтвердить",
                color=VkKeyboardColor.POSITIVE,
                payload={"type": "confirm", "title": f"{title}",
                         "time": f"{date}"},
            )

            self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                  message=MESS_REMINDER_RECEIVED_NO_TIME.substitute(title=title, time=date),
                                  random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard())

        else:
            title = ' '.join(a[1]).capitalize()
            time = a[0].strftime('%d.%m.%Y в %H:%M')

            keyboard = VkKeyboard(one_time=False, inline=True)
            keyboard.add_callback_button(
                label="Подтвердить",
                color=VkKeyboardColor.POSITIVE,
                payload={"type": "confirm", "title": f"{title}",
                         "time": f"{time}"}
            )

            self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                  message=MESS_REMINDER_RECEIVED.substitute(title=title, time=time),
                                  random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard())
