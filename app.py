import telebot
from telebot import types
from datetime import datetime
import redis
from user import User
import sys
import os
from dotenv import load_dotenv

load_dotenv()

prefix = os.environ.get("PREFIX", "PREFIX_")
token = os.environ.get("TOKEN")
# TODO: mv starttime to .env
# starttime = os.environ.get("PREFIX", "PREFIX_")

starttime = datetime(2023, 11, 7, 12)

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
r.set("prefix", str(prefix))

locations = [
    {"id": 0, "name": "Др", "location": "Шишкин Лес", "password": "111"},
    {"id": 1, "name": "Др2", "location": "Шишкин Лес2", "password": "222"},
    {"id": 2, "name": "Др3", "location": "Шишкин Лес3", "password": "333"},
]
r.set("locations", len(locations))


bot = telebot.TeleBot(token)


def ingame_m(message):
    bot.send_message(message.chat.id, "Вы в игре!")


# def stage(userId):
#     stage = r.lrange(userId, 0, 3)
#     return stQue[int(stage[1])][int(stage[0])]
# def genpass():
#     return "0"


@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, "Привет ✌️ ")
    bot.send_message(message.chat.id, "Для начала игры нажмите /run")
    print(message.chat.id)


@bot.message_handler(commands=["run"])
def run_m(message):
    # Тут по идее надо тупо отбивать всё, что не является персональным чатом, но лан
    if datetime.now() > starttime:
        user = User(r, int(message.from_user.id))
        if user.isEnd():
            bot.send_message(message.chat.id, "Посмеялись, а теперь бегом на финиш!")
        elif user.inGame():
            ingame_m(message)
        else:
            bot.send_message(message.chat.id, "Сейчас начнём!")
            bot.send_message(
                message.chat.id,
                f"Следующий этап — # {locations[user.location()]['location']}",
            )
            bot.send_message(
                message.chat.id,
                "Пройдите этап и присылай пароль для следующего уровня!",
            )
    else:
        bot.send_message(message.chat.id, "Игра ещё не началась")
    del user


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    user = User(r, int(message.from_user.id))
    if not user.isEnd():
        if message.text == str(locations[user.location()]["password"]):
            user.switchStage()
            bot.reply_to(message, "Шикарно!")
            if user.isEnd():
                bot.send_message(
                    message.chat.id, "Наши поздравления! Ждём тебя на финише!"
                )
            else:
                bot.send_message(
                    message.chat.id,
                    f"Отправляйтесь на следующую локацию: \n {locations[user.location()]['location']}",
                )

        else:
            bot.reply_to(message, "Это не похоже на правильный пароль!")
    else:
        bot.send_message(message.chat.id, "Здорово! Иди на финиш уже)")
    del user


@bot.message_handler(commands=["help"])
def help_m(message):
    bot.send_message(
        message.chat.id, "Здесь должна была быть справка, но её (пока) нет"
    )


bot.infinity_polling()
