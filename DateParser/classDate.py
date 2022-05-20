from calendar import monthrange
from datetime import datetime, timedelta


class Date:
    """
    Класс обработанной в алгоритме даты.
    """

    def __init__(self) -> None:
        cur_date = self.get_current_date()

        self.year = cur_date.year
        self.month = cur_date.month
        self.day = cur_date.day

        self.hour = 0
        self.minute = 0

        self.changed_time = False
        self.changed_date = False

    @classmethod
    def get_current_date(cls) -> datetime:
        """
        Получить текущую дату и время.
        """
        return datetime.now()

    @classmethod
    def month_plus(cls, date: datetime) -> datetime:
        """
        Прибавить к дате 1 месяц.
        """
        try:
            date = date.replace(month=date.month + 1, day=1)
        except ValueError:
            date = date.replace(year=date.year + 1, month=1, day=1)
        return date

    def update_weekday(self, number: int, day: str) -> None:
        """
        Изменить день в зависимости от дня недели.
        :param number: 0: текущая неделя; 1: следующая неделя.
        :param day: понедельник/вторник...
        """
        convert_day = {'понедельник': 0,
                       'вторник': 1,
                       'среда': 2,
                       'четверг': 3,
                       'пятница': 4,
                       'суббота': 5,
                       'воскресенье': 6}

        compare_date = self.get_datetime()

        if number != 0:
            compare_date = compare_date + timedelta(days=1)
            while compare_date.weekday() != 0:
                compare_date = compare_date + timedelta(days=1)

        while convert_day[day.lower()] != compare_date.weekday():
            compare_date = compare_date + timedelta(days=1)

        self.update_year(compare_date.year)
        self.update_month(compare_date.month)
        self.update_day(compare_date.day)

    def update_month_word(self, month: str) -> None:
        """
        Изменить месяц по его названию в русском языке.
        """
        convert_month = {'январь': 1,
                         'февраль': 2,
                         'март': 3,
                         'апрель': 4,
                         'май': 5,
                         'июнь': 6,
                         'июль': 7,
                         'август': 8,
                         'сентябрь': 9,
                         'октябрь': 10,
                         'ноябрь': 11,
                         'декабрь': 12}

        compare_date = self.get_datetime()

        while convert_month[month.lower()] != compare_date.month:
            compare_date = self.month_plus(compare_date)

        self.update_year(compare_date.year)
        self.update_month(compare_date.month)
        self.update_day(compare_date.day)

    def after_weeks(self, n: int) -> None:
        """
        Прибавить n-ное количество недель к дате.
        """
        compare_date = self.get_datetime()

        compare_date = compare_date + timedelta(days=7 * n)

        self.update_year(compare_date.year)
        self.update_month(compare_date.month)
        self.update_day(compare_date.day)

    def after_days(self, n: int) -> None:
        """
        Прибавить n-ное количество дней к дате.
        """
        compare_date = self.get_datetime()

        compare_date = compare_date + timedelta(days=n)

        self.update_year(compare_date.year)
        self.update_month(compare_date.month)
        self.update_day(compare_date.day)

    def update_year(self, year: int) -> None:
        """
        Обновить год в дате.
        """
        self.changed_date = True
        self.year = year

    def update_month(self, month: int) -> None:
        """
        Обновить месяц в дате.
        """
        self.changed_date = True
        self.month = month

    def update_day(self, day: int) -> None:
        """
        Обновить день в дате.
        """
        self.changed_date = True
        self.day = day

    def update_hour(self, hour: int, check_now=False) -> None:
        """
        Обновить час в дате.
        """
        self.changed_time = True

        if check_now:
            if self.get_datetime().replace(hour=hour) < datetime.now():
                self.after_days(1)

        self.hour = hour

    def update_minute(self, minute: int) -> None:
        """
        Обновить минуты в дате.
        """
        self.changed_time = True
        self.minute = minute

    def repair_date(self) -> None:
        """
        Починка даты перед преобразованием в datetime.

        Например, 61 минута преобразовывается в 1 час и 1 минуту и т.п.
        """
        while self.minute >= 60:
            self.minute -= 60
            self.hour += 1

        while self.hour >= 24:
            self.hour -= 24
            self.day += 1

        while self.day > monthrange(self.year, self.month)[1]:
            self.day -= monthrange(self.year, self.month)[1]
            self.month += 1

        while self.month > 12:
            self.month -= 12
            self.year += 1

    def get_datetime(self) -> datetime:
        """
        Получить текущую дату в формате datetime.
        """
        self.repair_date()
        return datetime(self.year, self.month, self.day, self.hour, self.minute)

    def get_changed(self) -> dict:
        """
        Были ли изменения в дате и во времени.

        Словарь вида: {'date': True/False, 'time': True/False}.

        True, если изменения были, False - не было.
        """
        return {'date': self.changed_date, 'time': self.changed_time}

    def set_default(self) -> None:
        """
        Обнулить дату и время внутри класса.
        """
        cur_date = self.get_current_date()
        self.year = cur_date.year
        self.month = cur_date.month
        self.day = cur_date.day
        self.hour = 0
        self.minute = 0
        self.changed_time = False
        self.changed_date = False

    def final_date(self) -> datetime:
        """
        Получить финальный вариант даты.
        """
        self.repair_date()

        if not self.changed_date and self.changed_time and self.get_datetime() < datetime.now():
            self.after_days(1)
            self.repair_date()

        return datetime(self.year, self.month, self.day, self.hour, self.minute)
