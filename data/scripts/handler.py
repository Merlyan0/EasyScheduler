import operator
from datetime import datetime

from vk_api.utils import get_random_id

from DateParser.parser import analyze_string
from data.scripts import messages
from data.scripts.functions import check_date
from data.scripts.keyboards import *
from data.scripts.messages import *


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

                all_r.append(str(n) + '. ' + title + i['check_date'].strftime(' // %d.%m.%Y | %H:%M') + ' \n')

            self.vk.messages.send(peer_id=peer_id,
                                  message=MESS_ALL_REMINDERS.substitute(all_r=''.join(all_r)),
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())

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
                          finished=False, created_date=datetime.now())

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

            self.db.set_date(event.object.message['from_id'], date.strftime('%Y-%m-%d %H:%M:%S'))

            self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                  message=MESS_CREATE_REMINDER_COMPLETED_2,
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())

        except (BaseException, ):
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

            self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                  message=MESS_REMINDER_RECEIVED_NO_TIME.substitute(title=title, time=time),
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())

            need_notification = False

        # DateParser обнаружил всё необходимое
        else:
            title = ' '.join(a[1]).capitalize()
            time = a[0].strftime('%d.%m.%Y в %H:%M')

            self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                  message=MESS_REMINDER_RECEIVED.substitute(title=title, time=time),
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())

        if need_add:
            self.db.add_to_db(title=title, author=event.object.message["from_id"],
                              check_date=a[0].strftime('%Y-%m-%d %H:%M:%S'), need_notification=need_notification,
                              finished=False)

    def send_reminders(self, date: str) -> None:
        """
        Отправить все подошедшие по времени напоминания.
        """
        for i in self.db.get_actual_reminders(date):
            title = i['title'].encode('unicode-escape').replace(b'\\\\', b'\\').decode('unicode-escape')

            self.vk.messages.send(user_id=i['author'],
                                  message=MESS_REMIND.substitute(title=title),
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())

    @classmethod
    def get_message(cls, message: str) -> str:
        """
        Получить сообщение по названию переменной.
        """
        return getattr(messages, message)
