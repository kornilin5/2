"""
Этот модуль содержит класс Bot, реализующий функционал бота для ВКонтакте.
"""

import time
import traceback

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

from commands import commands
from config import third_party_id, third_party_id_two, token


class Bot:
    """
    Класс Bot реализует функционал бота для ВКонтакте.
    """

    def __init__(self, key, blocker, checker, manager):
        self.token = key
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)
        self.spam_checker = checker
        self.user_blocker = blocker
        self.user_ids = manager

    def generate_dialog_link(self, user_id):
        """
        Генерирует ссылку на диалог с пользователем.
        """
        return f'https://vk.com/gim43062018?sel={user_id}'

    def send_message(self, event, message, is_admin=None):
        """
        Отправляет сообщение пользователю или администратору.
        """
        target_id = event.user_id if is_admin is None else is_admin
        self.vk.messages.send(
            user_id=target_id,
            random_id=get_random_id(),
            message=message,
        )

    def message_from_admin(self, event, message):
        """
        Обрабатывает сообщение от администратора.
        """
        user_id = event.user_id
        dialog_link = self.generate_dialog_link(user_id)
        message_from_admin = (
            f"Пользователь вызывает администратора через сообщение сообщества. "
            f"Ссылка на диалог: {user_id}: {dialog_link}")
        if message == "/adc":
            self.send_message(event, message_from_admin, third_party_id_two)
        elif message == '/adt':
            self.send_message(event, message_from_admin, third_party_id)
        else:
            return

    def user_message_handler(self, event, message, commands_list):
        """
        Обрабатывает сообщение от пользователя.
        """
        if message in commands_list and message.startswith('/'):
            self.send_message(event, commands_list[message])
            self.message_from_admin(event, message)

    def handle_event(self, event):
        """
        Обрабатывает событие от ВКонтакте.
        """
        if event.type == VkEventType.MESSAGE_NEW:
            user_id = event.user_id
            message = event.text.lower()
            self.user_ids.add_user(user_id)
            if self.user_blocker.check_for_block(
                    user_id, self.user_ids.get_user(user_id)):
                return
            if self.spam_checker.spam_check_in_minute(
                    user_id, self.user_ids.get_user(user_id)):
                return
            self.user_message_handler(event, message, commands)

    def run(self):
        """
        Запускает бота.
        """
        while True:
            try:
                for event in self.longpoll.listen():
                    self.handle_event(event)
            except (ConnectionError, vk_api.VkApiError) as e:
                traceback.print_exc()
                print(
                    f"Произошла ошибка: {e}. Бот будет перезапущен через 10 секунд."
                )
                time.sleep(10)
                continue


class UserBlocker:
    """
    Класс UserBlocker реализует функционал блокировки пользователей.
    """

    def __init__(self, manager):
        self.banned_users = {}
        self.current_time = time.time()
        self.manager = manager

    def block_user(self, user_id):
        """
        Блокирует пользователя на 60 секунд.
        """
        self.current_time = float(time.time())
        self.banned_users[user_id] = self.current_time + 60
        print(f'{self.banned_users} - это список забаненных пользователей')

    def check_for_block(self, user_id, user):
        """
        Проверяет, заблокирован ли пользователь.
        """
        current = float(time.time())
        print(f'User, который пришел: {user_id}')
        print(f'Список пользователей: {self.banned_users}')
        if user_id in self.banned_users:
            if current <= self.banned_users[user_id]:
                return True
            else:
                del self.banned_users[user_id]
                user.reset_attributes()
                return False
        else:
            return False


class SpamCheckerManager:
    """
    Класс SpamCheckerManager реализует функционал проверки спама.
    """

    def __init__(self, blocker, manager):
        self.command_limit = 3
        self.command_limit_interval = 60
        self.user_blocker = blocker
        self.user_manager = manager
        self.start_time = time.time()

    def spam_check_in_minute(self, user_id, user_object):
        """
        Проверяет, является ли сообщение пользователя спамом.
        """
        difference_time = user_object.last_request_time - user_object.first_message_time
        try:
            if (user_object.count >= self.command_limit
                    and difference_time <= self.command_limit_interval):
                self.user_blocker.block_user(user_id)
                print('Условия спама сработали')
                return True
            else:
                user_object.count += 1
                user_object.last_request_time = time.time()
                print('Условия спама не сработали')
                return False
        except (TypeError, ValueError) as e:
            print(f"Ошибка в spam_check_in_minute: {e}")
            return False


class UserManager:
    """
    Класс UserManager реализует функционал управления пользователями.
    """

    def __init__(self):
        self.users = {}

    def add_user(self, user_id):
        """
        Добавляет пользователя в систему.
        """
        if user_id not in self.users:
            self.users[user_id] = User()
        else:
            return

    def get_user(self, user_id):
        """
        Возвращает объект пользователя по его ID.
        """
        return self.users.get(user_id)

    def update_user_attributes(self, user_id, **kwargs):
        """
        Обновляет атрибуты пользователя.
        """
        user = self.users[user_id]
        for attr, value in kwargs.items():
            setattr(user, attr, value)


class User:
    """
    Класс User представляет объект пользователя.
    """

    def __init__(self):
        self.first_time_message = True
        self.first_message_time = time.time()
        self.last_request_time = time.time()
        self.count = 0

    def reset_attributes(self):
        """
        Сбрасывает атрибуты пользователя.
        """
        self.first_message_time = time.time()
        self.last_request_time = time.time()
        self.count = 0


user_manager = UserManager()
user_blocker = UserBlocker(user_manager)
spam_checker = SpamCheckerManager(user_blocker, user_manager)
bot = Bot(token, user_blocker, spam_checker, user_manager)
bot.run()
