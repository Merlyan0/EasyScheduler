from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# главное меню
KB_MAIN_MENU = VkKeyboard(one_time=False)

KB_MAIN_MENU.add_button('&#128195; Список напоминаний')

KB_MAIN_MENU.add_line()
KB_MAIN_MENU.add_button('&#128221; Ручной режим', color=VkKeyboardColor.SECONDARY)

KB_MAIN_MENU.add_line()
KB_MAIN_MENU.add_button('&#9881; Настройки', color=VkKeyboardColor.PRIMARY)


# меню ручного ввода
KB_MANUAL_MODE = VkKeyboard(one_time=False)

KB_MANUAL_MODE.add_button('&#128221; Создать напоминание', color=VkKeyboardColor.SECONDARY)
KB_MANUAL_MODE.add_button('&#9989; Завершить напоминание', color=VkKeyboardColor.SECONDARY)

KB_MANUAL_MODE.add_line()
KB_MANUAL_MODE.add_button('&#128281; Главное меню')


# меню возврата в главное меню
KB_BACK = VkKeyboard(one_time=False)

KB_BACK.add_button('&#128281; Главное меню')
