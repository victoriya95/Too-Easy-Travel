import logging
import sys

import telebot
from telebot import types, formatting
from telebot.types import InputMediaPhoto

import api

bot = telebot.TeleBot('6095050306:AAEsvO8Vdvb69Pc5w9v2rcT2gBh66l4c_I0')


class SearchParams:
    def __init__(self, instruction):
        self.instruction = instruction
        self.country = None
        self.town = None
        self.count = None
        self.show_photo = None
        self.count_photo = None


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start', 'lowprice', 'highprice'])
def send_welcome(message):
    if message.text in ["/start", "/help"]:
        bot.reply_to(message, "Hi there, I am EchoBot.\n"
                              "I am here to echo your kind words back to you.\n"
                              "Just say anything nice and I'll say the exact same thing to you!")
    elif message.text == "/lowprice" or '/highprice':
        msg = bot.reply_to(message, "Пожалуйста введите страну, где находится город: ")
        search_params = SearchParams(message.text)
        bot.register_next_step_handler(msg, read_country, search_params=search_params)
    else:
        bot.send_message(message.from_user.id, "Unknown message")


def read_country(message, search_params):
    search_params.country = message.text
    logging.info(f"ID: {message.message_id}. Target country: {message.text}")
    msg = bot.reply_to(message, "В каком городе будем искать?")
    bot.register_next_step_handler(msg, read_town, search_params=search_params)


def read_town(message, search_params):
    search_params.town = message.text
    logging.info(f"ID: {message.message_id}. Target town: {message.text}")
    msg = bot.reply_to(message, "Сколько отелей вывести?")
    bot.register_next_step_handler(msg, read_hotel_count, search_params=search_params)


def read_hotel_count(message, search_params):
    count = message.text

    if not count.isdigit():
        msg = bot.reply_to(message, "Пожалуйста, введите число отелей цифрой. Сколько отелей вывести?")
        bot.register_next_step_handler(msg, read_hotel_count, search_params=search_params)
        return

    search_params.count = count
    logging.info(f"ID: {message.message_id}. Search hotel count: {count}")

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("Да", "Нет")
    msg = bot.reply_to(message, "Загрузить фотографии для каждого отеля?", reply_markup=markup)
    bot.register_next_step_handler(msg, read_photo, search_params=search_params)


def read_photo(message, search_params):
    photo = message.text

    if photo not in ["Да", "Нет"]:
        msg = bot.reply_to(message, "Пожалуйста введите 'Да' или 'Нет'. Загрузить фотографии для каждого отеля?")
        bot.register_next_step_handler(msg, read_photo, search_params=search_params)
        return

    elif photo == 'Да':
        search_params.show_photo = photo
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add("1", '2', '3', '4', '5', '6')
        msg = bot.reply_to(message, "Какое количество фото загрузить?", reply_markup=markup)
        bot.register_next_step_handler(msg, read_count_photo, search_params=search_params)

    else:
        search_params.show_photo = photo
        search_params.count_photo = '0'
        bot.reply_to(message, "Идет поиск...")
        search_hotel(message, search_params)

    logging.info(f"ID: {message.message_id}. Load photos: {photo}")


def read_count_photo(message, search_params):
    count_photo = message.text
    logging.info(f"ID: {message.message_id}. Search hotel count: {count_photo}")

    search_params.count_photo = count_photo
    bot.reply_to(message, "Идет поиск...")
    search_hotel(message, search_params)


def search_hotel(message, search_params):
    region_id = api.search_region_id(message.message_id, search_params.country, search_params.town)

    if not region_id:
        bot.send_message(message.from_user.id, f"Город или страна не найдены. Пожалуйста, повторите поиск сначала.")
        return

    hotels = api.search_hotels(region_id[0], region_id[1], search_params)

    for hotel in hotels:
        data_hotel = api.info_hotels(hotel.id, search_params)

        bot.send_message(message.from_user.id,
                         f"*• Название отеля*:   {hotel.name}. \n\n*• Адрес отеля*:   {data_hotel[0]}. \n\n*• Цена*:   {hotel.price}. ",
                         parse_mode="Markdown")

        bot.send_photo(message.from_user.id, photo=data_hotel[-1], caption=formatting.mbold("Местоположение на карте"),
                       parse_mode="MarkdownV2")

        if search_params.show_photo == "Да":
            lisi_jpeg = []
            bot.send_message(message.from_user.id, f"\n*Фото отеля*:\n", parse_mode="Markdown")
            for i in range(search_params.count_photo):
                lisi_jpeg.append(telebot.types.InputMediaPhoto(data_hotel[1][i]))

            bot.send_media_group(message.from_user.id, lisi_jpeg)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(asctime)s %(levelname)s %(message)s")

    bot.set_my_commands(
        commands=[
            telebot.types.BotCommand("/start", "Start work with bot"),
            telebot.types.BotCommand("/help", "Show help"),
            telebot.types.BotCommand("/lowprice", "Поиск дешевых отелей!"),
            telebot.types.BotCommand("/highprice", "Поиск дорогих отелей!")
        ]
    )
    # Enable saving next step handlers to file "./.handlers-saves/step.save".
    # Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
    # saving will hapen after delay 2 seconds.
    bot.enable_save_next_step_handlers(delay=2)

    # Load next_step_handlers from save file (default "./.handlers-saves/step.save")
    # WARNING It will work only if enable_save_next_step_handlers was called!
    bot.load_next_step_handlers()

    bot.infinity_polling()
