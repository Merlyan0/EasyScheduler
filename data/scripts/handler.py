import json
import operator
from datetime import datetime, timedelta

from vk_api.utils import get_random_id

from DateParser.parser import analyze_string

from data.scripts import messages
from data.scripts.messages import *

from data.scripts.functions import check_date
from data.scripts.keyboards import *


class BotHandler:

    def __init__(self, vk, db) -> None:
        """
        Обработчик различных команд бота.
        :vk: VkApiMethod
        :db: DataBase class
        """
        self.vk = vk
        self.db = db

    def start(self, peer_id: int) -> None:
        """
        Функция, приветствующая пользователя при начале общения.
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=MESS_WELCOME,
                              random_id=get_random_id(),
                              keyboard=KB_MAIN_MENU.get_keyboard())

    def main_menu(self, peer_id: int) -> None:
        """
        Работа главного меню.
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=MESS_MAIN_MENU,
                              random_id=get_random_id(),
                              keyboard=KB_MAIN_MENU.get_keyboard())

    def settings(self, peer_id: int) -> None:
        """
        Работа настроек.
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=MESS_SETTINGS,
                              random_id=get_random_id(),
                              keyboard=KB_BACK.get_keyboard())

    def manual_mode(self, peer_id: int) -> None:
        """
        Работа меню ручного ввода.
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=MESS_MANUAL_MODE,
                              random_id=get_random_id(),
                              keyboard=KB_MANUAL_MODE.get_keyboard())

    def finish_step1(self, peer_id: int) -> None:
        """
        Отметить напоминания завершённым: шаг 1
        """
        a = self.db.get_author_reminders(peer_id)

        if a != ():
            a.sort(key=operator.itemgetter('check_date'))
            all_r, n = list(), 0

            for i in a:
                n += 1
                title = i['title'].encode('unicode-escape').replace(b'\\\\', b'\\').decode('unicode-escape')

                if i['need_notification'] == 0:
                    all_r.append(str(n) + '. ' + title + i['check_date'].strftime(' // %d.%m.%Y') + ' \n')
                else:
                    all_r.append(str(n) + '. ' + title + i['check_date'].strftime(' // %d.%m.%Y | %H:%M') + ' \n')

            self.vk.messages.send(peer_id=peer_id,
                                  message=MESS_ALL_REMINDERS.substitute(all_r=''.join(all_r)),
                                  random_id=get_random_id(),
                                  keyboard=KB_BACK.get_keyboard())

            self.vk.messages.send(peer_id=peer_id,
                                  message=MESS_HOW_TO_REMOVE,
                                  random_id=get_random_id())

        else:
            self.vk.messages.send(peer_id=peer_id,
                                  message=MESS_NO_REMINDERS,
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())

    def finish_step2(self, event) -> None:
        """
        Отметить напоминание завершённым: шаг 2
        """
        a = self.db.get_author_reminders(event.object.message['peer_id'])

        if a != ():
            a.sort(key=operator.itemgetter('check_date'))
            all_r, n = list(), 0

            try:
                to_delete = list(map(int, event.object.message["text"].split()))

                for i in a:
                    n += 1

                    if n in to_delete:
                        all_r.append(i['id'])

                if not all_r:
                    self.vk.messages.send(peer_id=event.object.message['peer_id'],
                                          message=MESS_FINISH_ID_ERROR,
                                          random_id=get_random_id(),
                                          keyboard=KB_MAIN_MENU.get_keyboard())
                    return

                self.db.set_finished(all_r)

                self.vk.messages.send(peer_id=event.object.message['peer_id'],
                                      message=MESS_SUCCESSFUL_FINISH,
                                      random_id=get_random_id(),
                                      keyboard=KB_MAIN_MENU.get_keyboard())

            except (BaseException,):
                self.main_menu(event.object.message['peer_id'])

    def timetable(self, peer_id: int, date: datetime) -> None:
        """
        Вывод расписание какого-либо пользователя.
        """
        a = self.db.get_author_date_reminders(peer_id, date)

        if a != ():
            a.sort(key=operator.itemgetter('check_date'))
            general, with_time = list(), list()

            for i in a:
                title = i['title'].encode('unicode-escape').replace(b'\\\\', b'\\').decode('unicode-escape')

                if i['need_notification'] == 0 and i['check_date'].strftime('%H:%M') == '00:00':
                    general.append('-  "' + title + '" \n')
                else:
                    with_time.append('-  "' + title + '"' + i['check_date'].strftime(' // %H:%M') + ' \n')

            self.vk.messages.send(peer_id=peer_id,
                                  message=MESS_TIMETABLE.substitute(general=''.join(general),
                                                                    with_time=''.join(with_time)),
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())
        else:
            self.vk.messages.send(peer_id=peer_id,
                                  message=MESS_NO_REMINDERS,
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())

    def create_manually_step1(self, peer_id: int) -> None:
        """
        Создание напоминания вручную: первое сообщение.
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=MESS_CREATE_REMINDER,
                              random_id=get_random_id(),
                              keyboard=KB_BACK.get_keyboard())

    def create_manually_step2(self, event) -> None:
        """
        Создание напоминания вручную: введено название напоминания.
        """
        self.db.add_to_db(title=event.object.message["text"],
                          author=event.object.message["from_id"],
                          check_date=datetime.now().strftime('%Y-%m-%d 00:00:00'),
                          need_notification=False)

        self.vk.messages.send(peer_id=event.object.message["peer_id"],
                              message=MESS_CREATE_REMINDER_COMPLETED_1,
                              random_id=get_random_id(),
                              keyboard=KB_MAIN_MENU.get_keyboard())

    def create_manually_step3(self, event) -> None:
        """
        Создание напоминания вручную: введена дата.
        """
        date = event.object.message["text"]

        try:
            date = check_date(date)
            now_date = datetime.now().strftime('%d.%m.%Y %H:%M')
            user_date = date.strftime('%d.%m.%Y %H:%M')

            if date < datetime.now():
                self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                      message=MESS_DATE_NOW_ERROR.substitute(now_date=now_date,
                                                                             user_date=user_date),
                                      random_id=get_random_id(),
                                      keyboard=KB_MAIN_MENU.get_keyboard())

            else:
                self.db.set_date(event.object.message['from_id'], date.strftime('%Y-%m-%d %H:%M:%S'))

                self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                      message=MESS_CREATE_REMINDER_COMPLETED_2,
                                      random_id=get_random_id(),
                                      keyboard=KB_MAIN_MENU.get_keyboard())

        except (BaseException,):
            self.reminder_analyzer(event)

    def reminder_analyzer(self, event) -> None:
        """
        Проанализировать строку на предмет налиичия напоминания.
        """
        need_add = True
        title = ''
        need_notification = True

        a = analyze_string(event.object.message["text"].lower())

        # DateParser вернул сообщение об ошибке
        if a[0] == 'Ошибка':
            self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                  message=f"&#10060; {a[0]} \n\n{a[1]}",
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())

            need_add = False

        # DateParser не нашел даты и времени в сообщении
        elif a[2]['date'] is False and a[2]['time'] is False:
            title = ' '.join(a[1]).capitalize()

            self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                  message=MESS_REMINDER_RECEIVED_NO_DATE.substitute(title=title),
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())

            need_notification = False

        # DateParser не нашел времени в сообщении
        elif a[2]['time'] is False:
            title = ' '.join(a[1]).capitalize()
            time = a[0].strftime('%d.%m.%Y')

            now_date = datetime.now().strftime('%d.%m.%Y %H:%M')
            user_date = a[0].strftime('%d.%m.%Y %H:%M')

            if a[0] < datetime.now():
                self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                      message=MESS_DATE_NOW_ERROR.substitute(now_date=now_date,
                                                                             user_date=user_date),
                                      random_id=get_random_id(),
                                      keyboard=KB_MAIN_MENU.get_keyboard())

                need_add = False

            else:
                self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                  message=MESS_REMINDER_RECEIVED_NO_TIME.substitute(title=title, time=time),
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())

            need_notification = False

        # DateParser обнаружил всё необходимое
        else:
            title = ' '.join(a[1]).capitalize()
            time = a[0].strftime('%d.%m.%Y в %H:%M')

            now_date = datetime.now().strftime('%d.%m.%Y %H:%M')
            user_date = a[0].strftime('%d.%m.%Y %H:%M')

            if a[0] < datetime.now():
                self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                      message=MESS_DATE_NOW_ERROR.substitute(now_date=now_date,
                                                                             user_date=user_date),
                                      random_id=get_random_id(),
                                      keyboard=KB_MAIN_MENU.get_keyboard())

                need_add = False

            else:
                self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                      message=MESS_REMINDER_RECEIVED.substitute(title=title, time=time),
                                      random_id=get_random_id(),
                                      keyboard=KB_MAIN_MENU.get_keyboard())

        if need_add:
            self.db.add_to_db(title=title, author=event.object.message["from_id"],
                              check_date=a[0].strftime('%Y-%m-%d %H:%M:%S'), need_notification=need_notification)

    def send_reminders(self, date: str) -> None:
        """
        Отправить все подошедшие по времени напоминания.
        """
        for i in self.db.get_actual_reminders(date):
            title = i['title'].encode('unicode-escape').replace(b'\\\\', b'\\').decode('unicode-escape')

            keyboard = VkKeyboard(one_time=False, inline=True)

            keyboard.add_callback_button(
                label="Завершить",
                color=VkKeyboardColor.SECONDARY,
                payload={"type": "set_finish", "id": i['id']})

            keyboard.add_line()

            keyboard.add_callback_button(
                label="Отложить на 5 мин.",
                color=VkKeyboardColor.SECONDARY,
                payload={"type": "set_delayed", "id": i['id']})

            self.vk.messages.send(user_id=i['author'],
                                  message=MESS_REMIND.substitute(title=title),
                                  random_id=get_random_id(),
                                  keyboard=keyboard.get_keyboard())

    def set_delayed(self, event, reminder_id: int) -> None:
        c_m_i = event["conversation_message_id"]
        prev_mess = self.vk.messages.getByConversationMessageId(peer_id=event["peer_id"],
                                                                conversation_message_ids=c_m_i)
        prev_mess = prev_mess['items'][0]["text"]

        if self.db.get_reminder(reminder_id)['check_date'] + timedelta(minutes=5) <= datetime.now():
            keyboard = VkKeyboard(one_time=False, inline=True)

            keyboard.add_callback_button(
                label="Завершить",
                color=VkKeyboardColor.SECONDARY,
                payload={"type": "set_finish", "id": reminder_id})

            self.vk.messages.edit(peer_id=event["peer_id"],
                                  message=prev_mess,
                                  conversation_message_id=event["conversation_message_id"],
                                  keyboard=keyboard.get_keyboard())

            self.vk.messages.sendMessageEventAnswer(
                event_id=event["event_id"],
                user_id=event["user_id"],
                peer_id=event["peer_id"],
                event_data=json.dumps({"type": "show_snackbar", "text": "Ошибка."}))

        else:
            self.vk.messages.edit(peer_id=event["peer_id"],
                                  message=prev_mess + '\n\n&#128276; Повтор через 5 минут.',
                                  conversation_message_id=event["conversation_message_id"])

            self.vk.messages.sendMessageEventAnswer(
                event_id=event["event_id"],
                user_id=event["user_id"],
                peer_id=event["peer_id"],
                event_data=json.dumps({"type": "show_snackbar", "text": "Напоминание отложено."}))

            self.db.set_delayed(reminder_id)

    def set_finished(self, event, reminder_id: int) -> None:
        c_m_i = event["conversation_message_id"]
        prev_mess = self.vk.messages.getByConversationMessageId(peer_id=event["peer_id"],
                                                                conversation_message_ids=c_m_i)
        prev_mess = prev_mess['items'][0]["text"]

        self.vk.messages.edit(peer_id=event["peer_id"],
                              message=prev_mess + '\n\n&#127383; Напоминание завершено.',
                              conversation_message_id=event["conversation_message_id"])

        self.vk.messages.sendMessageEventAnswer(
            event_id=event["event_id"],
            user_id=event["user_id"],
            peer_id=event["peer_id"],
            event_data=json.dumps({"type": "show_snackbar", "text": "Напоминание завершено."}))

        self.db.set_finished([reminder_id, ])

    @classmethod
    def get_message(cls, message: str) -> str:
        """
        Получить сообщение по названию переменной.
        """
        return getattr(messages, message)
