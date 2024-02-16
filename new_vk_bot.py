import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import time
from config import token, third_party_id, third_party_id_two
from commands import commands
import traceback


class Bot:

    def __init__(self, token, user_blocker, spam_checker, user_manager):
        self.token = token
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)
        self.spam_checker = spam_checker
        self.user_blocker = user_blocker
        self.user_ids = user_manager

    def generate_dialog_link(self, user_id):
        return f'https://vk.com/gim43062018?sel={user_id}'

    def send_message(self, event, message, is_admin=None):

        if is_admin == None:
            self.vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message=message,
            )
        else:
            self.vk.messages.send(
                user_id=is_admin,
                random_id=get_random_id(),
                message=message,
            )

    def message_from_user(self, event, message, commands):
        if message in commands and message.startswith('/'):
            user_id = event.user_id
            dialog_link = self.generate_dialog_link(user_id)
            message_from_admnin = f"Пользователь вызывает администратора через сообщение сообщества. Ссылка на диалог: {user_id}: {dialog_link}"
            self.send_message(event, commands[message])
            if message == "/adc":
                self.send_message(event, message_from_admnin,
                                  third_party_id_two)
            if message == '/adt':
                self.send_message(event, message_from_admnin, third_party_id)

    def handle_event(self, event):
        if event.type == VkEventType.MESSAGE_NEW:
            user_id = event.user_id
            user_chat = event.from_chat
            message = event.text.lower()
            self.user_ids.add_user(user_id)
            # Проверяем пользователя на блокировку
            if self.user_blocker.check_for_block(
                    user_id, self.user_ids.get_user(user_id)):
                return
            if self.spam_checker.spam_check_in_minute(
                    user_id, self.user_ids.get_user(user_id)):
                return
            self.message_from_user(event, message, commands)

    def run(self):
        while True:
            try:
                for event in self.longpoll.listen():
                    self.handle_event(event)
            except Exception as e:
                traceback.print_exc()
                print(
                    f"Произошла ошибка: {e}. Бот будет перезапущен через 10 секунд."
                )
                time.sleep(10)
                continue


# Класс блокера реализован правильно.
class UserBlockinger:

    def __init__(self, user_manager):
        self.banned_users = {}
        self.current_time = time.time()
        self.user_manager = user_manager

    def block_user(self, user_id):
        self.current_time = float(time.time())
        self.banned_users[user_id] = self.current_time + 60
        print(f'{self.banned_users} - eto spisok zabanenix polzovatelei')

    def check_for_block(self, user_id, user):
        current = float(time.time())
        print(f'User kotorii prishel {user_id}')
        print(f'Spisok polzovatele {self.banned_users}')
        if user_id in self.banned_users:
            if current <= self.banned_users[user_id]:
                return True
            else:  # Удаление пользователя из словаря, если время блокировки истекло.
                del self.banned_users[user_id]
                user.reset_attributes()
                return False
        else:
            return False


class SpamCheckerManeger:

    def __init__(self, user_blocker, user_manager):
        self.command_limit = 3
        self.command_limit_interval = 60
        self.user_blocker = user_blocker
        self.user_manager = user_manager
        self.start_time = time.time()

    def spam_check_in_minute(self, user_id, user_object):
        try:
            print(
                f'eto PARAMETRI {user_object.count}, {user_object.last_request_time - user_object.first_message_time}'
            )
            if user_object.count >= self.command_limit and user_object.last_request_time - user_object.first_message_time <= self.command_limit_interval:
                self.user_blocker.block_user(user_id)
                print('ysloviya spama srabotali')
                return True

            else:
                user_object.count += 1
                user_object.last_request_time = time.time()
                print('ysloviya spama ne srabotali')
                return False

        except Exception as e:
            print(f"Ошибка в spam_check_in_minute: {e}")
            return False


class UserManager:

    def __init__(self):
        self.users = {}

    def add_user(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = User()
        else:
            return

    def get_user(self, user_id):
        return self.users.get(user_id)

    def update_user_attributes(self, user_id, **kwargs):
        user = self.users[user_id]  # Получаем объект пользователя по его ID
        for attr, value in kwargs.items():
            setattr(user, attr, value)


class User:

    def __init__(self):
        self.first_time_message = True
        self.first_message_time = time.time()
        self.last_request_time = time.time()
        self.count = 0

    def reset_attributes(self):
        self.first_message_time = time.time()
        self.last_request_time = time.time()
        self.count = 0


user_manager = UserManager()
user_blocker = UserBlockinger(user_manager)
spam_checker = SpamCheckerManeger(user_blocker, user_manager)
bot = Bot(token, user_blocker, spam_checker, user_manager)
bot.run()
