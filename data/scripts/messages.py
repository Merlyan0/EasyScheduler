from string import Template

MESS_MAIN_MENU = "Главное меню"

MESS_SETTINGS = "Скоро тут появятся настройки"

MESS_WELCOME = 'Добро пожаловать в бота, который напомнит о важных делах. \n\n Чтобы создать напоминание ' \
               'введите его в текстовом виде, например, полить цветы через 2 часа.'

MESS_CREATE_REMINDER = "Хорошо. Введите название напоминания."

MESS_CREATE_REMINDER_COMPLETED_1 = """Отлично! Напоминание создано. \n
                                   Если необходимо, введите дату и время, когда необходимо напомнить. \n
                                   Формат ввода: день.месяц.год часы:минуты \n
                                   Если каких-то пунктов из даты вам не надо (например, года и месяцв),
                                   то можно ввести: день часы:минуты."""

MESS_CREATE_REMINDER_COMPLETED_2 = "Готово! К напоминанию добавлена дата."

MESS_REMINDER_RECEIVED = Template(f"""&#9989; Напоминание создано: \n
                                   "$title" // $time """)

MESS_REMINDER_RECEIVED_NO_TIME = Template("""&#9989; Напоминание "$title" добавлено в Ваше расписание на $time.""")

MESS_REMINDER_RECEIVED_NO_DATE = Template("""&#9989; Напоминание "$title" добавлено в Ваше расписание на сегодня.""")

MESS_REMIND = Template("&#9200; $title")
