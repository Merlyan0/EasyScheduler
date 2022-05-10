from string import Template

MESS_MAIN_MENU = "Главное меню"

MESS_SETTINGS = "Скоро тут появятся настройки"

MESS_CREATE_REMINDER = "Хорошо. Введите название напоминания."

MESS_CREATE_REMINDER_COMPLETED_1 = """Отлично! Напоминание создано. \n
                                   Если необходимо, введите дату и время, когда необходимо напомнить. \n
                                   Формат ввода: день.месяц.год часы:минуты \n
                                   Если каких-то пунктов из даты вам не надо (например, года и месяцв),
                                   то можно ввести: день часы:минуты."""

MESS_REMINDER_CONFIRMED = Template(f"""&#9989; Напоминание подтверждено! \n
                          -> $title \n
                          -> Дата: $time. \n
                          Напомню вам в указанную дату и за 15 минут до нёё.
                          Этот параметр можно поменять в настройках.""")
