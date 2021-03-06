# прочее
import os
from datetime import datetime
from io import BytesIO
import requests

# работа с изображениями
from PIL import Image, ImageDraw, ImageFont

# работа с аудио
import speech_recognition as sr
from pydub import AudioSegment


r = sr.Recognizer()  # распознаватель голоса


def check_date(date: str) -> datetime:
    """
    Проверить дату на соответствие формату.
    :date: Дата в формате день.месяц.год.
    """
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

    return a


def draw_timetable(reminders: list, date: datetime, authors_name: str) -> bytes:
    """
    Отрисовать фотографию расписания пользователя.
    :reminders: список со словарями с напоминаниями.
    :authors_name: имя автора напоминаний.
    """
    addition_amount = len(reminders) - 1

    basic = Image.open('data/images/timetable3.jpg')

    addition_1 = Image.open('data/images/addition_1.jpg')
    addition_2 = Image.open('data/images/addition_2.jpg')

    plus = addition_1.size[1] - 20 if addition_amount % 2 == 1 else -20
    timetable = Image.new('RGB', (basic.size[0], basic.size[1] + addition_amount // 2 *
                                  (addition_1.size[1] + addition_2.size[1]) + plus), color='white')

    timetable.paste(basic, (0, 0))

    n = 0
    for i in range(addition_amount):
        if i % 2 == 0:
            timetable.paste(addition_1, (0, basic.size[1] - 2 + addition_1.size[1] * n + addition_2.size[1] * n))
            n += 1
        else:
            timetable.paste(addition_2, (0, basic.size[1] - 2 + addition_1.size[1] * n + addition_2.size[1] * (n - 1)))

    font = ImageFont.truetype("data/fonts/framd.ttf", 34)
    drawer = ImageDraw.Draw(timetable)
    drawer.text((271, 15), date.strftime('%d.%m.%Y'), font=font, fill='#808080')

    font = ImageFont.truetype("data/fonts/framd.ttf", 19)
    drawer.text((547, 30), "EasyScheduler", font=font, fill='#808080')
    drawer.text((704, 30), datetime.now().strftime('%d.%m.%Y'), font=font, fill='#808080')
    drawer.text((864, 30), authors_name, font=font, fill='#808080')

    font1 = ImageFont.truetype("data/fonts/cambria.ttf", 12)
    font2 = ImageFont.truetype("data/fonts/cambria.ttf", 22)

    for i in range(len(reminders)):
        if reminders[i]['need_notification'] == 0:
            drawer.text((22, 103 + 35 * i), '———', font=font1, fill='black')
        else:
            drawer.text((22, 103 + 35 * i), reminders[i]['check_date'].strftime('%H:%M'), font=font1, fill='black')
        drawer.text((110, 95 + 35 * i), reminders[i]['title'], font=font2, fill='black')

    output = BytesIO()
    timetable.save(output, format='JPEG')

    return output.getvalue()


def speech_recognizer(audio: str) -> str:
    """
    Распознать аудио сообщения.
    :audio: ссылка на mp3 аудио в ВК.
    """
    doc = requests.get(audio)
    filename = audio.split('/')[-1].split('.')[0]

    os.makedirs('temp', exist_ok=True)

    with open(f'temp/{filename}.mp3', 'wb') as f:
        f.write(doc.content)

    sound = AudioSegment.from_mp3(f'temp/{filename}.mp3')
    sound.export(f'temp/{filename}.wav', format="wav")

    audio_ex = sr.AudioFile(f'temp/{filename}.wav')

    with audio_ex:
        audio_data = r.record(audio_ex)

    os.remove(f'temp/{filename}.mp3')
    os.remove(f'temp/{filename}.wav')

    return r.recognize_google(audio_data, language='ru-RU')


def get_date_from_message(message: str) -> datetime:
    """
    Получить дату из сообщения, если возможно.
    """
    a = list(map(int, message.split('.')))
    return datetime(a[2] if a[2] >= 2000 else 2000 + a[2], a[1], a[0])
