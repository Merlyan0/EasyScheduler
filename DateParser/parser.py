import pymorphy2

from DateParser.classDate import Date

# знаки пунктуации
punctuation = ('.', ',', ';', ':', '?', '!', '-', '(', ')', '"', '\'')

# слова-спутники даты
token_words = ['год',

               'январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль',
               'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь',

               'понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье',

               'спустя',
               'через',
               'выходной',
               'минута',
               'час',
               'день',
               'неделя',
               'месяц',
               'этот', 'текущий', 'нынешний',
               'ближайший', 'грядущий',
               'следующий', 'будущий',
               'послезавтра',
               'завтра',
               'сегодня',
               'утро',
               'полдень',
               'вечер', 'вечером',
               'ночь',
               'половина',
               'четверть',

               'полночь',

               'ежедневно',
               'еженедельно',
               'ежемесячно',
               'ежегодно']

# слова прошедшего времени
past_words = ['назад', 'прошлый', 'прошедший', 'предыдущий', 'вчера', 'позавчера']

# морфологический анализатор
morph = pymorphy2.MorphAnalyzer()

# последовательность обработки строки
plan = ['month', 'relative_day', 'year', 'relative_date', 'weekday', 'time', 'day', 'repeat']

# экземпляр класса Date с найденной датой
parsed_date = Date()


def analyze_string(starting_text) -> tuple:
    # обнуляем класс даты
    parsed_date.set_default()

    # раздел предложения на отдельные слова
    start_list = starting_text.split()

    # инициализация используемых в методе списков
    temp_list1, temp_list2, to_delete = list(), list(), list()

    # удаление знаков препинания с конца слов
    for i in start_list:
        while i.endswith(punctuation):
            i = i[:-1]
        i = i.lower()
        temp_list1.append(i)

    # удаление знаков препинания с начала слов
    for i in temp_list1:
        while i.startswith(punctuation):
            i = i[1:]
        i = i.lower()
        temp_list2.append(i)

    # список слов в начальной форме
    normal_forms = [morph.parse(i)[0].normal_form for i in temp_list2]

    # выполнение пунктов плана
    for p in range(len(plan)):

        # анализ каждого слова
        for i in range(len(normal_forms)):

            # если найдено слово, относящееся к прошедшему времени
            if normal_forms[i] in past_words:
                return 'Ошибка', \
                       'Похоже, вы ввели слова, относящиеся к прошедшему времени (вчера, на прошлой неделе и т.д.) \n' \
                       'Нельзя поставить напоминание на уже прошедшую дату.'

            # если найдены слова-спутники даты
            elif normal_forms[i] in token_words:

                # обработка месяца
                if plan[p] == 'month':

                    # вид обрабатываемой строки: {...} января|февраля...
                    if normal_forms[i] in ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август',
                                           'сентябрь', 'октябрь', 'ноябрь', 'декабрь']:
                        parsed_date.update_month_word(normal_forms[i])

                        to_delete.append(i)

                # сегодня, завтра, послезавтра
                elif plan[p] == 'relative_day':

                    # вид обрабатываемой строки: послезавтра
                    if normal_forms[i] == 'послезавтра':
                        parsed_date.update_day(parsed_date.get_current_date().day + 2)
                        to_delete.append(i)

                    # вид обрабатываемой строки: завтра
                    elif normal_forms[i] == 'завтра':
                        parsed_date.update_day(parsed_date.get_current_date().day + 1)
                        to_delete.append(i)

                    # вид обрабатываемой строки: сегодня
                    elif normal_forms[i] == 'сегодня':
                        parsed_date.update_day(parsed_date.get_current_date().day)
                        to_delete.append(i)

                # обработка выражений вида: через..., на следующей неделе...
                elif plan[p] == 'relative_date':

                    # вид обрабатываемой строки: через неделю
                    if i - 1 != -1 and normal_forms[i - 1] == 'через' and normal_forms[i] == 'неделя':
                        parsed_date.after_weeks(1)
                        to_delete.append(i - 1)
                        to_delete.append(i)

                    # вид обрабатываемой строки: через месяц
                    elif i - 1 != -1 and normal_forms[i - 1] == 'через' and normal_forms[i] == 'месяц':
                        return 'Ошибка', 'Попробуйте указать явно количество дней ' \
                                         '(например, через 30 дней) ' \
                                         'или конкретную дату (например, 6 октября).'

                    # вид обрабатываемой строки: через день
                    elif i - 1 != -1 and normal_forms[i - 1] == 'через' and normal_forms[i] == 'день':
                        parsed_date.after_days(1)
                        to_delete.append(i - 1)
                        to_delete.append(i)

                # проверка введённых дней недели
                elif plan[p] == 'weekday':
                    number = -1

                    if normal_forms[i] in ['понедельник', 'вторник', 'среда', 'четверг',
                                           'пятница', 'суббота', 'воскресенье']:

                        # вид обрабатываемой строки: следующий|будущий понедельник|вторник...
                        if i - 1 != -1 and normal_forms[i - 1] in ['следующий', 'будущий']:
                            number = 1

                        # вид обрабатываемой строки: ближайший|грядущий... понедельник|вторник...
                        elif i - 1 != -1 and normal_forms[i - 1] in ['ближайший', 'грядущий', 'этот',
                                                                     'текущий', 'нынешний']:
                            number = 0

                        # вид обрабатываемой строки: в понедельник|вторник...
                        elif i - 1 != -1 and normal_forms[i - 1] == 'в':
                            number = 0

                        # вид обрабатываемой строки: в следующий понедельник|вторник...
                        if i - 2 >= 0 and normal_forms[i - 2] == 'в' and number != -1:
                            to_delete.append(i - 2)

                        # обновление даты
                        if number != -1:
                            parsed_date.update_weekday(number, normal_forms[i])
                            to_delete.append(i - 1)
                            to_delete.append(i)

                # обработка времени в словесном формате без чисел (в полночь, в час...)
                elif plan[p] == 'time':

                    # вид обрабатываемой строки: в полночь
                    if i - 1 != -1 and normal_forms[i - 1] == 'в' and normal_forms[i] == 'полночь':
                        parsed_date.update_hour(0)
                        parsed_date.update_minute(0)
                        to_delete.append(i - 1)
                        to_delete.append(i)

                    # вид обрабатываемой строки: в час дня
                    elif i - 1 != -1 and i + 1 < len(normal_forms) and normal_forms[i - 1] == 'в' \
                            and normal_forms[i] == 'час' and normal_forms[i + 1] == 'день':
                        parsed_date.update_hour(13, check_now=True)
                        to_delete.append(i - 1)
                        to_delete.append(i)
                        to_delete.append(i + 1)

                    # вид обрабатываемой строки: в час ночи
                    elif i - 1 != -1 and i + 1 < len(normal_forms) and normal_forms[i - 1] == 'в' \
                            and normal_forms[i] == 'час' and normal_forms[i + 1] == 'ночь':
                        parsed_date.update_hour(1, check_now=True)
                        to_delete.append(i - 1)
                        to_delete.append(i)
                        to_delete.append(i + 1)

                    # вид обрабатываемой строки: в час
                    elif i - 1 != -1 and normal_forms[i - 1] == 'в' and normal_forms[i] == 'час':
                        parsed_date.update_hour(13, check_now=True)
                        to_delete.append(i - 1)
                        to_delete.append(i)

                    # вид обрабатываемой строки: через минуту
                    elif i - 1 != -1 and normal_forms[i - 1] == 'через' and normal_forms[i] == 'минута':
                        parsed_date.update_hour(parsed_date.get_current_date().hour)
                        parsed_date.update_minute(parsed_date.get_current_date().minute + 1)
                        to_delete.append(i - 1)
                        to_delete.append(i)

                    # вид обрабатываемой строки: через час
                    elif i - 1 != -1 and normal_forms[i - 1] == 'через' and normal_forms[i] == 'час':
                        parsed_date.update_minute(parsed_date.get_current_date().minute)
                        parsed_date.update_hour(parsed_date.get_current_date().hour + 1)
                        to_delete.append(i - 1)
                        to_delete.append(i)

                elif plan[p] == 'repeat':

                    # вид обрабатываемой строки: каждый день
                    if i - 1 != -1 and normal_forms[i - 1] == 'каждый' and normal_forms[i] == 'день':
                        parsed_date.repeat_every = 1
                        to_delete.append(i - 1)
                        to_delete.append(i)

                    # вид обрабатываемой строки: каждый понедельник|вторник
                    elif i - 1 != -1 and normal_forms[i - 1] == 'каждый' and normal_forms[i] in \
                            ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']:
                        parsed_date.repeat_every = 7
                        parsed_date.update_weekday(0, normal_forms[i])
                        to_delete.append(i - 1)
                        to_delete.append(i)

                    # вид обрабатываемой строки: каждую неделю
                    elif i - 1 != -1 and normal_forms[i - 1] == 'каждый' and normal_forms[i] == 'неделя':
                        parsed_date.repeat_every = 7
                        to_delete.append(i - 1)
                        to_delete.append(i)

                    # вид обрабатываемой строки: каждый месяц
                    elif i - 1 != -1 and normal_forms[i - 1] == 'каждый' and normal_forms[i] == 'месяц':
                        parsed_date.repeat_every = -3
                        to_delete.append(i - 1)
                        to_delete.append(i)

                    # вид обрабатываемой строки: каждый год
                    elif i - 1 != -1 and normal_forms[i - 1] == 'каждый' and normal_forms[i] == 'год':
                        parsed_date.repeat_every = -2
                        to_delete.append(i - 1)
                        to_delete.append(i)

                    # вид обрабатываемой строки: ежедневно
                    elif normal_forms[i] == 'ежедневно':
                        parsed_date.repeat_every = 1
                        to_delete.append(i)

                    # вид обрабатываемой строки: еженедельно
                    elif normal_forms[i] == 'еженедельно':
                        parsed_date.repeat_every = 7
                        to_delete.append(i)

                    # вид обрабатываемой строки: ежемесячно
                    elif normal_forms[i] == 'ежемесячно':
                        parsed_date.repeat_every = -3
                        to_delete.append(i)

                    # вид обрабатываемой строки: ежегодно
                    elif normal_forms[i] == 'ежегодно':
                        parsed_date.repeat_every = -2
                        to_delete.append(i)

            # обработка чисел
            elif temp_list2[i].isdigit():

                # обработка введенного года
                if plan[p] == 'year':

                    # вид обрабатываемой строки: {2022 - 2099} год
                    if 2022 <= int(temp_list2[i]) < 2099 and normal_forms[i + 1] == 'год':
                        parsed_date.update_year(int(temp_list2[i]))
                        to_delete.append(i)

                        if i + 1 < len(normal_forms) and normal_forms[i + 1] == 'год':
                            to_delete.append(i + 1)

                elif plan[p] == 'relative_date':

                    # вид обрабатываемой строки: через ... недель
                    if i - 1 != -1 and i + 1 < len(normal_forms) and \
                            normal_forms[i - 1] == 'через' and normal_forms[i + 1] == 'неделя':
                        parsed_date.after_weeks(int(temp_list2[i]))
                        to_delete.append(i - 1)
                        to_delete.append(i)
                        to_delete.append(i + 1)

                    # вид обрабатываемой строки: через ... месяцев
                    elif i - 1 != -1 and i + 1 < len(normal_forms) and \
                            normal_forms[i - 1] == 'через' and normal_forms[i + 1] == 'месяц':
                        return 'Ошибка', 'Попробуйте указать явно количество дней ' \
                                         '(например, через 30 дней) ' \
                                         'или конкретную дату (например, 6 октября).'

                    # вид обрабатываемой строки: через ... дней
                    elif i - 1 != -1 and i + 1 < len(normal_forms) and \
                            normal_forms[i - 1] == 'через' and normal_forms[i + 1] == 'день':
                        parsed_date.after_days(int(temp_list2[i]))
                        to_delete.append(i - 1)
                        to_delete.append(i)
                        to_delete.append(i + 1)

                elif plan[p] == 'repeat':

                    # вид обрабатываемой строки: каждые ... дней
                    if i - 1 != -1 and i + 1 < len(normal_forms) and \
                            normal_forms[i - 1] == 'каждый' and normal_forms[i + 1] == 'день':
                        parsed_date.repeat_every = int(temp_list2[i])
                        to_delete.append(i - 1)
                        to_delete.append(i)
                        to_delete.append(i + 1)

                    # вид обрабатываемой строки: каждые ... недель
                    elif i - 1 != -1 and i + 1 < len(normal_forms) and \
                            normal_forms[i - 1] == 'каждый' and normal_forms[i + 1] == 'неделя':
                        parsed_date.repeat_every = int(temp_list2[i]) * 7
                        to_delete.append(i - 1)
                        to_delete.append(i)
                        to_delete.append(i + 1)

                    # вид обрабатываемой строки: каждые ... лет
                    elif i - 1 != -1 and i + 1 < len(normal_forms) and \
                            normal_forms[i - 1] == 'каждый' and normal_forms[i + 1] == 'год':
                        parsed_date.repeat_every = int(temp_list2[i]) * 365
                        to_delete.append(i - 1)
                        to_delete.append(i)
                        to_delete.append(i + 1)

                # числа от 1 до 60
                if 1 <= int(temp_list2[i]) <= 60:

                    # обработка года
                    if plan[p] == 'year':

                        # вид обрабатываемой строки: {1-60} год
                        if i + 1 < len(normal_forms) and normal_forms[i + 1] == 'год':
                            parsed_date.update_year(2000 + int(temp_list2[i]))
                            to_delete.append(i + 1)
                            to_delete.append(i)

                    # обработка времени
                    elif plan[p] == 'time':

                        # вид обрабатываемой строки: в {1-23} часов
                        if i - 1 != -1 and i + 1 < len(normal_forms) and normal_forms[i - 1] == 'в' \
                                and normal_forms[i + 1] == 'час':

                            if not 1 <= int(temp_list2[i]) <= 23:
                                return 'Ошибка', 'Вы ввели час, равный числу, большему 23.'

                            parsed_date.update_hour(int(temp_list2[i]))
                            to_delete.append(i - 1)
                            to_delete.append(i)
                            to_delete.append(i + 1)

                        # вид обрабатываемой строки: в {1-12} вечера
                        elif i - 1 != -1 and i + 1 < len(normal_forms) and normal_forms[i - 1] == 'в' \
                                and normal_forms[i + 1] == 'вечер':

                            if not 1 <= int(temp_list2[i]) <= 12:
                                return 'Ошибка', 'Вы ввели час во второй половине дня, равный числу, большему 12.'

                            parsed_date.update_hour(12 + int(temp_list2[i]))
                            to_delete.append(i - 1)
                            to_delete.append(i)
                            to_delete.append(i + 1)

                        # вид обрабатываемой строки: в {1-12} утра
                        elif i - 1 != -1 and i + 1 < len(normal_forms) and normal_forms[i - 1] == 'в' \
                                and normal_forms[i + 1] == 'утро':

                            if not 1 <= int(temp_list2[i]) <= 12:
                                return 'Ошибка', 'Вы ввели час в первой половине дня, равный числу, большему 12.'

                            parsed_date.update_hour(int(temp_list2[i]))
                            to_delete.append(i - 1)
                            to_delete.append(i)
                            to_delete.append(i + 1)

                        # вид обрабатываемой строки: через {1-60} минут
                        elif i - 1 != -1 and i + 1 < len(normal_forms) and normal_forms[i - 1] == 'через' and \
                                normal_forms[i + 1] == 'минута':
                            parsed_date.update_minute(parsed_date.get_current_date().minute + int(temp_list2[i]))
                            parsed_date.update_hour(parsed_date.get_current_date().hour)
                            to_delete.append(i - 1)
                            to_delete.append(i)
                            to_delete.append(i + 1)

                        # вид обрабатываемой строки: через {1-23} час(-а)
                        elif i - 1 != -1 and i + 1 < len(normal_forms) and normal_forms[i - 1] == 'через' and \
                                normal_forms[i + 1] == 'час':

                            if not 1 <= int(temp_list2[i]) <= 23:
                                return 'Ошибка', 'Вы ввели час, равный числу, большему 23.'

                            parsed_date.update_minute(parsed_date.get_current_date().minute)
                            parsed_date.update_hour(parsed_date.get_current_date().hour + int(temp_list2[i]))
                            to_delete.append(i - 1)
                            to_delete.append(i)
                            to_delete.append(i + 1)

                        # вид обрабатываемой строки: {1-60} минут
                        elif i + 1 < len(normal_forms) and normal_forms[i + 1] == 'минута':
                            parsed_date.update_minute(int(temp_list2[i]))
                            to_delete.append(i)
                            to_delete.append(i + 1)

                        # вид обрабатываемой строки: в {1-23}
                        elif i - 1 != -1 and normal_forms[i - 1] == 'в':

                            if not 1 <= int(temp_list2[i]) <= 23:
                                return 'Ошибка', 'Вы ввели час, равный числу, большему 23.'

                            if (i + 1 < len(normal_forms) and normal_forms[i + 1] != 'год') or \
                                    i + 1 == len(normal_forms):
                                parsed_date.update_hour(int(temp_list2[i]))
                                to_delete.append(i)
                                to_delete.append(i - 1)

                    # обработка дня
                    elif plan[p] == 'day':

                        # вид обрабатываемой строки: {1-31} января|февраля...
                        if i + 1 < len(normal_forms) and normal_forms[i + 1] in ['январь', 'февраль', 'март',
                                                                                 'апрель',
                                                                                 'май', 'июнь', 'июль', 'август',
                                                                                 'сентябрь', 'октябрь', 'ноябрь',
                                                                                 'декабрь']:
                            parsed_date.update_day(int(temp_list2[i]))
                            to_delete.append(i)
                            to_delete.append(i + 1)

                        # вид обрабатываемой строки: {1-31} числа
                        elif i + 1 < len(normal_forms) and normal_forms[i + 1] == 'число':
                            parsed_date.update_day(int(temp_list2[i]))
                            to_delete.append(i)
                            to_delete.append(i + 1)

            # вид обрабатываемой строки: (в) 12:34
            elif len(temp_list2[i].split(':')) == 2:
                if parsed_date.check_time(temp_list2[i].split(':')[0], temp_list2[i].split(':')[1]):
                    to_delete.append(i)
                    if i - 1 != -1 and normal_forms[i - 1] == 'в':
                        to_delete.append(i - 1)

            # вид обрабатываемой строки: (в) 12-34
            elif len(temp_list2[i].split('-')) == 2:
                if parsed_date.check_time(temp_list2[i].split('-')[0], temp_list2[i].split('-')[1]):
                    to_delete.append(i)
                    if i - 1 != -1 and normal_forms[i - 1] == 'в':
                        to_delete.append(i - 1)

            # вид обрабатываемой строки: (в) 12.34
            elif len(temp_list2[i].split('.')) == 2:
                if parsed_date.check_time(temp_list2[i].split('.')[0], temp_list2[i].split('.')[1]):
                    to_delete.append(i)
                    if i - 1 != -1 and normal_forms[i - 1] == 'в':
                        to_delete.append(i - 1)

            # вид обрабатываемой строки: день.месяц.год
            elif len(temp_list2[i].split('.')) == 3:
                if parsed_date.check_date(temp_list2[i].split('.')[0], temp_list2[i].split('.')[1],
                                          temp_list2[i].split('.')[2]):
                    to_delete.append(i)

    # напоминание
    finished_list = list()

    # запись самого напоминания
    for i in range(len(temp_list2)):
        if i not in to_delete:
            finished_list.append(start_list[i])

    if len(finished_list) == 0:
        return 'Ошибка', 'Не удалось распознать напоминание в сообщении.'

    finished_list[0] = finished_list[0].capitalize()

    return parsed_date.final_date(), finished_list, parsed_date.get_changed(), parsed_date.repeat_every
