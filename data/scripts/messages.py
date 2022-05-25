from string import Template

MESS_MAIN_MENU = "Главное меню"

MESS_SETTINGS = "Этот раздел находится в разработке"

MESS_MANUAL_MODE = "Меню ручного ввода"

MESS_LOADING = "&#128257; Ваша задача выполняется..."

MESS_TIMETABLE = Template("&#8505; Ваши напоминания на сегодня: "
                          "\n\n&#128312; Общие: \n$general"
                          "\n&#128312; С указанием времени: \n$with_time")

MESS_DRAWING_TT = Template("&#8505; Созданное специально для Вас расписание ниже.\n\n"
                           "&#10071; Обратите внимание: вы можете создавать отграниченное количество расписаний в "
                           "день. Текущий лимит: $limit расписаний/день.")

MESS_MAX_SYMBOL = Template("&#8505; В вашем напоминании более $limit символов.\n\n"
                           "Мы всё равно добавили его в базу данных, но некоторые функции могут работать некорректно.")

MESS_AUDIO_CONVERTER = Template("&#8505; Ваше сообщение распознано: \n\n"
                                "$message\n\n"
                                "&#10071; Обратите внимание: вы можете распознавать отграниченное количество голосовых "
                                "сообщений в день. Текущий лимит: $limit сообщений/день.")

MESS_SUPPORT_1 = "➡ Если у Вас возникли вопросы, отправьте их следующим сообщением."

MESS_SUPPORT_2 = "&#9989; Ваше сообщение успешно отправлено. \n\n" \
                 "Мы ответим Вам в ближайшее время."

MESS_WELCOME = "Добро пожаловать в бота, который напомнит о важных делах. \n\n Чтобы создать напоминание, " \
               "введите его в текстовом виде, например, «полить цветы через 2 часа»."

MESS_NO_REMINDERS = "&#8505; Напоминаний не обнаружено."

MESS_ALL_REMINDERS = Template("&#8505; Напоминания, доступные для завершения: \n$all_r")

MESS_HOW_TO_REMOVE = "Для завершения одного/нескольких напоминаний введите их номера через пробел."

MESS_SUCCESSFUL_FINISH = "&#8505; Напоминания успешно завершены."

MESS_CREATE_REMINDER = "Хорошо. Введите название напоминания."

MESS_CREATE_REMINDER_COMPLETED_1 = "Отлично! Напоминание создано." \
                                   "\n\nЕсли необходимо, введите дату и время, когда необходимо напомнить." \
                                   "\nФормат ввода: день.месяц.год часы:минуты \n\n" \
                                   "Если каких-то пунктов из даты вам не надо (например, года и месяца), " \
                                   "то можно ввести: день часы:минуты."

MESS_CREATE_REMINDER_COMPLETED_2 = "Готово! К напоминанию добавлена дата."

MESS_REMINDER_RECEIVED = Template("&#9989; Напоминание создано: \n\n"
                                  "\"$title\" // $time ")

MESS_REMINDER_RECEIVED_NO_TIME = Template("&#9989; Напоминание \"$title\" добавлено в Ваше расписание на $time.")

MESS_REMINDER_RECEIVED_NO_DATE = Template("&#9989; Напоминание \"$title\" добавлено в Ваше расписание на сегодня.")

MESS_REMIND = Template("&#9200; $title")

MESS_REMIND_REPEAT = Template("&#9200; $title\n\n"
                              "Это напоминание автоматически повторяется $repeat_every. "
                              "Если вы хотите завершить его, сделайте это вручную через меню \"Ручной режим\".")

# ошибки
MESS_STICKER_ERROR = "&#8505; Нельзя поставить стикер в качестве напоминания."

MESS_EMPTY_ERROR = "&#8505; Отправлено пустое сообщение. \n\n" \
                   "Попробуйте добавить текст."

MESS_UNKNOWN_ERROR = "&#10060; Неизвестная ошибка."

MESS_FINISH_ID_ERROR = "&#8505; Напоминаний с таким номером не обнаружено."

MESS_DATE_NOW_ERROR = Template("&#8505; Нельзя поставить напоминание на прошедшую дату.\n\n"
                               "Сейчас: $now_date\n"
                               "Вы ввели: $user_date")

# лимиты
MESS_DRAW_LIMIT = Template("&#10060; Лимит отрисовки расписания на сегодня исчерпан.\n\n"
                           "Текущий лимит: $limit расписаний/день. Вы использовали его полностью.")

MESS_VOICE_LIMIT = Template("&#10060; Лимит распознавания голосовых сообщений на сегодня исчерпан.\n\n"
                            "Текущий лимит: $limit расписаний/день. Вы использовали его полностью.")

