# прочее
import json
import operator
from datetime import datetime, timedelta
import requests

# VK API
from vk_api.utils import get_random_id

# скрипт анализа строки на наличие даты
from DateParser.parser import analyze_string, morph

# настройки из конфиг файла
from config import SUPPORT_ID, DRAW_LIMIT, MAX_SYMBOLS, VOICE_LIMIT

# сообщения
from data.scripts import messages
from data.scripts.messages import *

# доп. функции
from data.scripts.functions import check_date, draw_timetable, speech_recognizer

# клавиатуры
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

        # для последующего склонения
        self.day_word = morph.parse('день')[0]
        self.every_word = morph.parse('каждый')[0]

    def start(self, peer_id: int) -> None:
        """
        Функция, приветствующая пользователя при начале общения.
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=MESS_WELCOME,
                              random_id=get_random_id(),
                              keyboard=KB_MAIN_MENU.get_keyboard())

    def check_user_db(self, user_id: int) -> None:
        """
        Проверить наличие пользователя в БД.
        """
        self.db.add_user(user_id)

    def sticker_error(self, peer_id: int) -> None:
        """
        Вывести ошибку об использовании стикеров.
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=MESS_STICKER_ERROR,
                              random_id=get_random_id(),
                              keyboard=KB_MAIN_MENU.get_keyboard())

    def empty_error(self, peer_id: int) -> None:
        """
        Вывести ошибку о пустом сообщении.
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=MESS_EMPTY_ERROR,
                              random_id=get_random_id(),
                              keyboard=KB_MAIN_MENU.get_keyboard())

    def unknown_error(self, peer_id: int) -> None:
        """
        Возникла неизвестная ошибка.
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=MESS_UNKNOWN_ERROR,
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

    def support_step1(self, peer_id: int) -> None:
        """
        Работа команды помощи.
        """
        self.vk.messages.send(peer_id=peer_id,
                              message=MESS_SUPPORT_1,
                              random_id=get_random_id(),
                              keyboard=KB_BACK.get_keyboard())

    def support_step2(self, event) -> None:
        """
        Работа команды помощи.
        """
        from_id = "// ОТ: vk.com/id" + str(event.object.message['from_id']) + " //\n\n"
        decorate = "==========================\n"

        self.vk.messages.send(peer_id=SUPPORT_ID,
                              message=decorate + from_id + event.object.message['text'] + '\n' + decorate,
                              random_id=get_random_id())

        self.vk.messages.send(peer_id=event.object.message['peer_id'],
                              message=MESS_SUPPORT_2,
                              random_id=get_random_id(),
                              keyboard=KB_MAIN_MENU.get_keyboard())

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
            title = ' '.join(a[1])

            self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                  message=MESS_REMINDER_RECEIVED_NO_DATE.substitute(title=title),
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())

            need_notification = False

        # DateParser не нашел времени в сообщении
        elif a[2]['time'] is False:
            title = ' '.join(a[1])
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
            title = ' '.join(a[1])
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
            event_att = event.object.message["attachments"]
            attachments = list()

            # формирование вложений для БД
            for i in event_att:
                att_type = i['type']
                owner_id = str(i[att_type]['owner_id'])
                att_id = str(i[att_type]['id'])

                if att_type == 'audio':
                    attachments.append(att_type + owner_id + '_' + att_id)

                else:
                    access_key = i[att_type]['access_key']
                    attachments.append(att_type + owner_id + '_' + att_id + '_' + access_key)

            self.db.add_to_db(title=title, author=event.object.message["from_id"], attachments=', '.join(attachments),
                              check_date=a[0].strftime('%Y-%m-%d %H:%M:%S'), need_notification=need_notification,
                              repeat_every=a[3])

            if len(title) > MAX_SYMBOLS:
                self.vk.messages.send(peer_id=event.object.message["peer_id"],
                                      message=MESS_MAX_SYMBOL.substitute(limit=MAX_SYMBOLS),
                                      random_id=get_random_id(),
                                      keyboard=KB_MAIN_MENU.get_keyboard())

    def send_reminders(self, date: str) -> None:
        """
        Отправить все подошедшие по времени напоминания.
        """
        for i in self.db.get_actual_reminders(date, is_done=True):
            title = i['title'].encode('unicode-escape').replace(b'\\\\', b'\\').decode('unicode-escape')

            if i['repeat_every'] == -1:
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
                                      attachment=i['attachments'].split(', '),
                                      random_id=get_random_id(),
                                      keyboard=keyboard.get_keyboard())

                self.db.set_done(i['id'])

            else:
                if i['repeat_every'] == -2:
                    self.vk.messages.send(user_id=i['author'],
                                          message=MESS_REMIND_REPEAT.substitute(title=title,
                                                                                repeat_every='каждый год'),
                                          attachment=i['attachments'].split(', '),
                                          random_id=get_random_id())

                elif i['repeat_every'] == -3:
                    self.vk.messages.send(user_id=i['author'],
                                          message=MESS_REMIND_REPEAT.substitute(title=title,
                                                                                repeat_every='каждый месяц'),
                                          attachment=i['attachments'].split(', '),
                                          random_id=get_random_id())
                else:
                    e = self.every_word.make_agree_with_number(i['repeat_every']).word
                    d = self.day_word.make_agree_with_number(i['repeat_every']).word
                    e = e if e != 'каждых' else 'каждые'
                    repeat_every = e + ' ' + str(i['repeat_every']) + ' ' + d
                    self.vk.messages.send(user_id=i['author'],
                                          message=MESS_REMIND_REPEAT.substitute(title=title,
                                                                                repeat_every=repeat_every),
                                          attachment=i['attachments'].split(', '),
                                          random_id=get_random_id())

            self.db.repeat(i['id'])

    def set_delayed(self, event, reminder_id: int) -> None:
        """
        Установить напоминание отложенным на 5 минут.
        """
        try:
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

        except (BaseException,):
            self.unknown_error(event["peer_id"])

    def set_finished(self, event, reminder_id: int) -> None:
        """
        Установить напоминание завершённым.
        """
        try:
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

        except (BaseException,):
            self.unknown_error(event["peer_id"])

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
                                  keyboard=KB_TIMETABLE_MENU.get_keyboard())
        else:
            self.vk.messages.send(peer_id=peer_id,
                                  message=MESS_NO_REMINDERS,
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())

    def drawing_tt(self, peer_id: int, user: dict) -> None:
        """
        Прислать фотографию пользователю с его расписанием.
        """
        self.db.update_limits(peer_id)

        if self.db.get_user_draw_limit(peer_id) < DRAW_LIMIT:

            self.vk.messages.send(peer_id=peer_id,
                                  message=MESS_LOADING,
                                  random_id=get_random_id())

            a = self.db.get_author_date_reminders(peer_id, datetime.now())

            if a != ():
                a.sort(key=operator.itemgetter('check_date'))

                img = {'photo': ("file.jpeg", draw_timetable(a, user['first_name'] + ' ' + user['last_name']))}

                self.vk.messages.send(peer_id=peer_id,
                                      message=MESS_DRAWING_TT.substitute(limit=DRAW_LIMIT),
                                      attachment=self.upload_photo(peer_id, img),
                                      random_id=get_random_id())

                self.db.add_to_draw_limit(peer_id)

            else:
                self.vk.messages.send(peer_id=peer_id,
                                      message=MESS_NO_REMINDERS,
                                      random_id=get_random_id(),
                                      keyboard=KB_MAIN_MENU.get_keyboard())

        else:
            self.vk.messages.send(peer_id=peer_id,
                                  message=MESS_DRAW_LIMIT.substitute(limit=DRAW_LIMIT),
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())

    def audio_converter(self, peer_id: int, audio: str) -> str:
        """
        Обработка голосовых сообщений.
        """
        self.db.update_limits(peer_id)

        if self.db.get_user_voice_limit(peer_id) < VOICE_LIMIT:
            message = speech_recognizer(audio)

            self.vk.messages.send(peer_id=peer_id,
                                  message=MESS_AUDIO_CONVERTER.substitute(message=message, limit=VOICE_LIMIT),
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())

            self.db.add_to_voice_limit(peer_id)

            return message
        else:
            self.vk.messages.send(peer_id=peer_id,
                                  message=MESS_VOICE_LIMIT.substitute(limit=VOICE_LIMIT),
                                  random_id=get_random_id(),
                                  keyboard=KB_MAIN_MENU.get_keyboard())
            return ''

    def repeat_all(self) -> None:
        """
        Обновить дату в напоминаниях.
        """
        self.db.repeat_all()

    @classmethod
    def get_message(cls, message: str) -> str:
        """
        Получить сообщение по названию переменной.
        """
        return getattr(messages, message)

    def upload_photo(self, peer_id: int, img: dict) -> str:
        """
        Загрузить фото на сервер ВКонтакте.
        """
        data = self.vk.photos.getMessagesUploadServer(peer_id=peer_id)
        url = data['upload_url']

        r = requests.post(url, files=img)
        r = json.loads(r.text)

        server = r['server']
        photo = r['photo']
        photo_hash = r['hash']

        photo_id = self.vk.photos.saveMessagesPhoto(server=server, photo=photo, hash=photo_hash)
        photo_id = photo_id[0]

        photo_url = 'photo' + str(photo_id['owner_id']) + '_' + str(photo_id['id']) + '_' + \
                    str(photo_id['access_key'])

        return photo_url
