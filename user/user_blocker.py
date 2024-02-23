import time

class UserBlocker:
    """
    Класс UserBlocker реализует функционал блокировки пользователей.
    """
    DEFAULT_BLOCK_TIME_SECONDS = 60

    def __init__(self, manager):
        self.banned_users = {}
        self.manager = manager

    def block_user(self, user_id):
        """
        Блокирует пользователя на 60 секунд.
        """
        start_time = time.time()
        self.banned_users[
            user_id] = start_time + self.DEFAULT_BLOCK_TIME_SECONDS
        print(f'{self.banned_users[user_id]} - это забаненный пользователь')

    def remove_ban_and_reset_attributes(self, user_id, user_object):
        if user_id in self.banned_users:
            del self.banned_users[user_id]
            user_object.reset_attributes()

    def is_user_blocked(self, user_id):
        """
        Проверяет, заблокирован ли пользователь.
        """
        if user_id in self.banned_users:
            current_time = time.time()
            if current_time <= self.banned_users[user_id]:
                return True
            else:
                return False
