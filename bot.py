# прочее
import threading
import time
from datetime import datetime
from data.scripts.functions import get_date_from_message

# VK API
import vk_api
from vk_api.bot_longpoll import VkBotEventType

# работа с базой данных
from data.scripts.db import DataBase

# обработчик команд
from data.scripts.handler import BotHandler

# настройки из конфига
from config import *

# безопасный класс для подключения к LongPoll
from data.scripts.secureLongPoll import SecureVkBotLongPoll

# подключение к сервисам API ВКонтакте
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = SecureVkBotLongPoll(vk_session, GROUP_ID)

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

    if datetime.now().hour == 0 and datetime.now().minute == 0 and datetime.now().second == 0:
        handler.repeat_all()
        time.sleep(1)


# отправка подошедших по времени напоминаний
every_minute()

# все приходящие с сервера события
for event in longpoll.listen():

    # пришло новое сообщение
    if event.type == VkBotEventType.MESSAGE_NEW:

        try:

            # проверка пользователя в БД
            handler.check_user_db(event.object.message["from_id"])

            message = event.object.message["text"].lower()  # присланное сообщение
            peer_id = event.object.message["peer_id"]  # id диалога в боте
            attachments = event.object.message["attachments"]  # вложения

            # если пришел стикер
            if message == '' and attachments != [] and 'sticker' in attachments[0]:
                handler.sticker_error(peer_id)

            # если пришло голосовое сообщение
            elif message == '' and attachments != [] and 'audio_message' in attachments[0]:
                audio = event.object.message["attachments"][0]['audio_message']['link_mp3']
                message = handler.audio_converter(peer_id, audio)

                # если расшифрованное аудио не является пустым
                if message != '':
                    event.object.message["text"] = message
                    handler.reminder_analyzer(event)

            # если пришло пустое сообщение
            elif message == '':
                handler.empty_error(peer_id)

            # команда главного меню
            elif message in {'главная', '🔙 главное меню'}:
                handler.main_menu(peer_id)

            # команда настроек
            elif message in {'⚙ настройки', 'настройки'}:
                handler.settings(peer_id)

            # команда помощи
            elif message in {'❓ помощь', 'помощь', 'поддержка'}:
                handler.support_step1(peer_id)

            # команда перехода в ручное меню
            elif message in {'📝 ручной режим', 'ручной режим', 'ручной'}:
                handler.manual_mode(peer_id)

            # команда ручного создания напоминаний
            elif message in {'📝 создать напоминание', 'создать напоминание', 'создать'}:
                handler.create_manually_step1(peer_id)

            # команда просмотра расписания
            elif message in {'📃 список напоминаний', 'список', 'расписание'}:
                handler.timetable(peer_id, datetime.now())

            # команда завершения напоминания
            elif message in {'✅ завершить напоминание', 'завершить', 'завершить напоминание'}:
                handler.finish_step1(peer_id)

            # команда начать: приветствие пользователя
            elif message == 'начать':
                handler.start(peer_id)

            # команда отрисовки расписания
            elif message in {'⏏ генерация фото', 'генерация фото', 'генерация'}:
                handler.drawing_tt(peer_id, datetime.now(), vk.users.get(user_ids=event.object.message["from_id"])[0])

            # команда просмотра расписания на определенную дату
            elif message.startswith('расписание'):
                try:
                    date = get_date_from_message(message.split()[1])
                    handler.timetable(peer_id, date)

                except (BaseException, ):
                    handler.unknown_error(peer_id)

            # команда отрисовки расписания на определенную дату
            elif message.startswith('генерация'):
                try:
                    date = get_date_from_message(message.split()[1])
                    handler.drawing_tt(peer_id, date, vk.users.get(user_ids=event.object.message["from_id"])[0])

                except (BaseException, ):
                    handler.unknown_error(peer_id)

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

                # сообщение адресовано в поддержку
                if prev_mess == handler.get_message("MESS_SUPPORT_1"):
                    handler.support_step2(event)

                # сообщение для удаления напоминаний
                elif prev_mess == handler.get_message("MESS_HOW_TO_REMOVE"):
                    handler.finish_step2(event)

                # сообщение для ручного создания напоминания: название
                elif prev_mess == handler.get_message("MESS_CREATE_REMINDER"):
                    handler.create_manually_step2(event)

                # сообщение для ручного создания напоминания: дата
                elif prev_mess == handler.get_message("MESS_CREATE_REMINDER_COMPLETED_1"):
                    handler.create_manually_step3(event)

                # анализ строки на предмет содержания напоминания
                else:
                    handler.reminder_analyzer(event)

        except (BaseException,) as e:
            try:
                print(e)
                handler.unknown_error(event.object.message["peer_id"])

            except (BaseException,):
                print('Произошла неизвестная ошибка.')

    # нажата кнопка в inline меню
    elif event.type == VkBotEventType.MESSAGE_EVENT:

        try:
            # установить напоминание завершённым
            if event.object.payload.get("type") == "set_finish":
                handler.set_finished(event.object, event.object.payload.get("id"))

            # отложить напоминание на 5 минут
            elif event.object.payload.get("type") == "set_delayed":
                handler.set_delayed(event.object, event.object.payload.get("id"))

            # другая дата в расписании
            elif event.object.payload.get("type") == "other_date_timetable":
                handler.other_date_timetable(event.object)

            # другая дата в фото
            elif event.object.payload.get("type") == "other_date_painter":
                handler.other_date_painter(event.object)

        except (BaseException,) as e:
            try:
                print(e)
                handler.unknown_error(event.object.message["peer_id"])

            except (BaseException,):
                print('Произошла неизвестная ошибка.')
