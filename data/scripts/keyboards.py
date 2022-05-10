from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# главное меню
KB_MAIN_MENU = VkKeyboard(one_time=True)

KB_MAIN_MENU.add_button('&#128195; Список напоминаний')

KB_MAIN_MENU.add_line()
KB_MAIN_MENU.add_button('&#128221; Создать напоминание', color=VkKeyboardColor.SECONDARY)
KB_MAIN_MENU.add_button('&#9989; Завершить напоминание', color=VkKeyboardColor.SECONDARY)

KB_MAIN_MENU.add_line()
KB_MAIN_MENU.add_button('&#9881; Настройки', color=VkKeyboardColor.PRIMARY)


# меню возврата в главное меню
KB_BACK = VkKeyboard(one_time=True)

KB_BACK.add_button('&#128281; Главное меню')
