import json

from vk_api.utils import get_random_id

from data.scripts import messages

from data.scripts.keyboards import *
from data.scripts.messages import *


class BotHandler:
    def __init__(self, vk):
        self.vk = vk

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

    """
    ВНУТРЕННИЕ ФУНКЦИИ
    """
    @classmethod
    def get_message(cls, message):
        return getattr(messages, message)
