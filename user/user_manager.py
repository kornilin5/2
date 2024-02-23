import time


class UserManager:
    """
    Класс UserManager реализует функционал управления пользователями.
    """

    def __init__(self):
        self.users = {}

    def exists(self, user_id):
        return user_id in self.users

    def add(self, user_id):
        """
        Добавляет пользователя в систему.
        """
        self.users[user_id] = User()

    def fetch(self, user_id):
        """
        Возвращает объект пользователя по его ID.
        """
        return self.users.get(user_id)


class User:
    """
    Класс User представляет объект пользователя.
    """

    def __init__(self):
        self.id = +1
        self.first_message_time = time.time()
        self.last_message_time = time.time()
        self.message_count = 0

    def reset_attributes(self):
        """
        Сбрасывает атрибуты пользователя.
        """
        self.first_message_time = time.time()
        self.last_message_time = time.time()
        self.message_count = 0
