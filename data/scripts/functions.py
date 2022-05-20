from datetime import datetime
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


def check_date(date: str) -> datetime:
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


def draw_timetable(reminders: list, authors_name: str) -> bytes:
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
    drawer.text((271, 15), datetime.now().strftime('%d.%m.%Y'), font=font, fill='#808080')

    font = ImageFont.truetype("data/fonts/framd.ttf", 19)
    drawer.text((547, 30), "EasyScheduler", font=font, fill='#808080')
    drawer.text((704, 30), datetime.now().strftime('%d.%m.%Y'), font=font, fill='#808080')
    drawer.text((864, 30), authors_name, font=font, fill='#808080')

    font1 = ImageFont.truetype("data/fonts/cambria.ttf", 12)
    font2 = ImageFont.truetype("data/fonts/cambria.ttf", 22)

    for i in range(len(reminders)):
        drawer.text((22, 103 + 35 * i), reminders[i]['check_date'].strftime('%H:%M'), font=font1, fill='black')
        drawer.text((110, 95 + 35 * i), reminders[i]['title'], font=font2, fill='black')

    output = BytesIO()
    timetable.save(output, format='JPEG')

    return output.getvalue()
