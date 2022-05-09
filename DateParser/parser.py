import pymorphy2

from DateParser.classDate import Date

# знаки пунктуации
punctuation = ['.', ',', ';', ':', '?', '!', '-', '(', ')', '"', '\'']

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
               'четверть']

# слова прошедшего времени
past_words = ['назад', 'прошлый', 'прошедший', 'предыдущий', 'вчера', 'позавчера']

# морфологический анализатор
morph = pymorphy2.MorphAnalyzer()

# последовательность обработки строки
plan = ['month', 'relative_day', 'year', 'relative_date', 'weekday', 'time', 'day']

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
        for j in punctuation:
            while i.endswith(j):
                i = i[:-1]
            i = i.lower()
        temp_list1.append(i)

    # удаление знаков препинания с начала слов
    for i in temp_list1:
        for j in punctuation:
            while i.startswith(j):
                i = i[1:]
            i = i.lower()
        temp_list2.append(i)

    # список слов в начальной форме
    normal_forms = [morph.parse(i)[0].normal_form for i in temp_list2]

    for p in range(len(plan)):
        for i in range(len(normal_forms)):
            if normal_forms[i] in past_words:
                return 'Ошибка', \
                       'Похоже, вы ввели слова, относящиеся к прошедшему времени (вчера, на прошлой неделе и т.д.) \n' \
                       'Нельзя поставить напоминание на уже прошедшую дату.'

            if normal_forms[i] in token_words:

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

                    # вид обрабатываемой строки: завтра
                    elif normal_forms[i] == 'завтра':
                        parsed_date.update_day(parsed_date.get_current_date().day + 1)

                    # вид обрабатываемой строки: сегодня
                    elif normal_forms[i] == 'сегодня':
                        parsed_date.update_day(parsed_date.get_current_date().day)

                    to_delete.append(i)

                # обработка введенного года
                elif plan[p] == 'year':

                    # вид обрабатываемой строки: {2022 - 2099} год
                    if temp_list2[i].isdigit():
                        if 2022 <= int(temp_list2[i]) < 2099 and normal_forms[i + 1] == 'год':
                            parsed_date.update_year(int(temp_list2[i]))
                            to_delete.append(i)
                            if i + 1 < len(normal_forms) and normal_forms[i + 1] == 'год':
                                to_delete.append(i + 1)

                # обработка выражений вида: через..., на следующей неделе...
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
                        return 'Не удалось обработать запрос', 'Попробуйте указать явно количество дней ' \
                                                               '(например,через 30 дней)' \
                                                               'или конкретную дату (6 октября).'

                    # вид обрабатываемой строки: через ... дней
                    elif i - 1 != -1 and i + 1 < len(normal_forms) and \
                            normal_forms[i - 1] == 'через' and normal_forms[i + 1] == 'день':
                        parsed_date.after_days(int(temp_list2[i]))
                        to_delete.append(i - 1)
                        to_delete.append(i)
                        to_delete.append(i + 1)

                    # вид обрабатываемой строки: через неделю
                    if i - 1 != -1 and normal_forms[i - 1] == 'через' and normal_forms[i] == 'неделя':
                        parsed_date.after_weeks(1)
                        to_delete.append(i - 1)
                        to_delete.append(i)

                    # вид обрабатываемой строки: через месяц
                    elif i - 1 != -1 and normal_forms[i - 1] == 'через' and normal_forms[i] == 'месяц':
                        return 'Не удалось обработать запрос', 'Попробуйте указать явно количество дней ' \
                                                               '(например,через 30 дней)' \
                                                               'или конкретную дату (6 октября).'

                    # вид обрабатываемой строки: через день
                    elif i - 1 != -1 and normal_forms[i - 1] == 'через' and normal_forms[i] == 'день':
                        parsed_date.after_days(1)
                        to_delete.append(i - 1)
                        to_delete.append(i)

                # проверка введённых дней недели
                elif plan[p] == 'weekday':
                    number = -1

                    # вид обрабатываемой строки: следующий|будущий понедельник|вторник...
                    if i - 1 != -1 and normal_forms[i - 1] in ['следующий', 'будущий']:
                        number = 1
                        to_delete.append(i - 1)

                    # вид обрабатываемой строки: ближайший|грядущий... понедельник|вторник...
                    elif i - 1 != -1 \
                            and normal_forms[i - 1] in ['ближайший', 'грядущий', 'этот', 'текущий', 'нынешний'] \
                            and plan[p] == 'weekday':
                        number = 0
                        to_delete.append(i - 1)

                    # вид обрабатываемой строки: в понедельник|вторник...
                    elif i - 1 != -1 and normal_forms[i - 1] == 'в':
                        number = 0
                        to_delete.append(i - 1)

                    if number != -1 and normal_forms[i] in ['понедельник', 'вторник', 'среда', 'четверг',
                                                            'пятница', 'суббота', 'воскресенье']:
                        parsed_date.update_weekday(number, normal_forms[i])
                        to_delete.append(i)

            # обработка чисел 1-60
            if temp_list2[i].isdigit() and 1 <= int(temp_list2[i]) < 60:

                # обработка года
                if plan[p] == 'year':

                    # вид обрабатываемой строки: {1-59} год
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

                    # вид обрабатываемой строки: через {1-59} минут
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

                    # вид обрабатываемой строки: {1-59} минут
                    elif i + 1 < len(normal_forms) and normal_forms[i + 1] == 'минута':
                        parsed_date.update_minute(int(temp_list2[i]))
                        to_delete.append(i)
                        to_delete.append(i + 1)

                    # вид обрабатываемой строки: в {1-23}
                    elif i - 1 != -1 and normal_forms[i - 1] == 'в':

                        if not 1 <= int(temp_list2[i]) <= 23:
                            return 'Ошибка', 'Вы ввели час, равный числу, большему 23.'

                        parsed_date.update_hour(int(temp_list2[i]))
                        to_delete.append(i)
                        to_delete.append(i - 1)

                # обработка дня
                elif plan[p] == 'day':

                    # вид обрабатываемой строки: {1-31} января|февраля...
                    if i + 1 < len(normal_forms) and normal_forms[i + 1] in ['январь', 'февраль', 'март', 'апрель',
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
                parsed_date.update_hour(int(temp_list2[i].split(':')[0]))
                parsed_date.update_minute(int(temp_list2[i].split(':')[1]))
                to_delete.append(i)
                if i - 1 != -1 and normal_forms[i - 1] == 'в':
                    to_delete.append(i - 1)

    # запись всего, что осталось в финальный список
    finished_list = list()
    for i in range(len(temp_list2)):
        if i not in to_delete:
            finished_list.append(temp_list2[i])

    return parsed_date.get_datetime(), finished_list, parsed_date.get_changed()