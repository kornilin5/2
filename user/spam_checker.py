import time


class SpamCheckerManager:
    """
    Класс SpamCheckerManager реализует функционал проверки спама.
    """
    MESSAGE_LIMIT = 3
    MESSAGE_LIMIT_INTERVAL = 60

    def __init__(self, blocker, manager):
        self.user_blocker = blocker
        self.user_manager = manager

    def detect_spam(self, user_object):
        """
        Проверяет, является ли сообщение пользователя спамом.
        """
        difference_time = user_object.last_message_time - user_object.first_message_time
        if (user_object.message_count >= self.MESSAGE_LIMIT
                and difference_time <= self.MESSAGE_LIMIT_INTERVAL):
            print('Условия спама сработали')
            return True
        elif difference_time > self.MESSAGE_LIMIT_INTERVAL:
            user_object.reset_attributes()
            print(
                f' условие сработало, теперь у юзера такие параметры {user_object.first_message_time}, {user_object.last_message_time}, {user_object.message_count}'
            )
            return False
        else:
            user_object.message_count += 1
            user_object.last_message_time = time.time()
            print(
                f' {user_object.first_message_time}, {user_object.last_message_time}, {user_object.message_count}Условия спама не сработали'
            )
            return False
