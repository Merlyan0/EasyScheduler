from vk_api.bot_longpoll import VkBotLongPoll


class SecureVkBotLongPoll(VkBotLongPoll):
    """
    Безопасный класс для работы с VkBotLongPoll.
    """
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except (BaseException, ) as lp_error:
                print('error', lp_error)
