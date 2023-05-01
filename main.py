import logging
import sys

import telebot
from telebot import types, formatting

import api

bot = telebot.TeleBot('6095050306:AAEsvO8Vdvb69Pc5w9v2rcT2gBh66l4c_I0')


class SearchParams:
    def __init__(self):
        self.country = None
        self.town = None
        self.count = None
        self.show_photo = None
        self.count_photo = None
        self.sort_revers = False
        self.cost_min = 100.0
        self.cost_max = 10000.0
        self.distance_min = 0
        self.distance_max = 10000
        self.arrival = None
        self.departure = None


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start', 'lowprice', 'highprice', 'bestdeal'])
def send_welcome(message):
    if message.text in ["/start", "/help"]:
        bot.reply_to(message, "Hi there, I am EchoBot.\n"
                              "I am here to echo your kind words back to you.\n"
                              "Just say anything nice and I'll say the exact same thing to you!")
    elif message.text == "/lowprice":
        search_params = SearchParams()
        start_search(message, search_params)
    elif message.text == "/highprice":
        search_params = SearchParams()
        search_params.sort_revers = True
        start_search(message, search_params)
    elif message.text == "/bestdeal":
        search_params = SearchParams()
        msg = bot.reply_to(message, "Пожалуйста введите минимальную стоимость отеля")
        bot.register_next_step_handler(msg, min_cost, search_params=search_params)
    else:
        bot.send_message(message.from_user.id, "Unknown message")


def start_search(message, search_params):
    msg = bot.reply_to(message, "Пожалуйста введите страну, где находится город: ")
    bot.register_next_step_handler(msg, read_country, search_params=search_params)


def min_cost(message, search_params):
    if not message.text.isdigit():
        msg = bot.reply_to(message, "Пожалуйста, введите минимальную стоимость цифрой")
        bot.register_next_step_handler(msg, min_cost, search_params=search_params)
        return

    search_params.cost_min = float(message.text)
    msg = bot.reply_to(message, "Пожалуйста введите максимальную стоимость отеля")
    bot.register_next_step_handler(msg, max_cost, search_params=search_params)


def max_cost(message, search_params):
    if not message.text.isdigit():
        msg = bot.reply_to(message, "Пожалуйста, введите максимальную стоимость цифрой")
        bot.register_next_step_handler(msg, max_cost, search_params=search_params)
        return

    search_params.cost_max = float(message.text)
    msg = bot.reply_to(message, "Пожалуйста введите минимальное расстояние от центра")
    bot.register_next_step_handler(msg, min_dest, search_params=search_params)


def min_dest(message, search_params):
    if not message.text.isdigit():
        msg = bot.reply_to(message, "Пожалуйста, введите минимальное расстояние цифрой")
        bot.register_next_step_handler(msg, min_dest, search_params=search_params)
        return

    search_params.distance_min = float(message.text)
    msg = bot.reply_to(message, "Пожалуйста введите максимальное расстояние от центра")
    bot.register_next_step_handler(msg, max_dest, search_params=search_params)


def max_dest(message, search_params):
    if not message.text.isdigit():
        msg = bot.reply_to(message, "Пожалуйста, введите максимальное расстояние цифрой")
        bot.register_next_step_handler(msg, max_dest, search_params=search_params)
        return
    else:
        search_params.distance_max = float(message.text)
        start_search(message, search_params)


def read_country(message, search_params):
    search_params.country = message.text
    logging.info(f"User: {message.from_user.username}. Target country: {message.text}")
    msg = bot.reply_to(message, "В каком городе будем искать?")
    bot.register_next_step_handler(msg, read_town, search_params=search_params)


def read_town(message, search_params):
    search_params.town = message.text
    logging.info(f"User: {message.from_user.username}. Target town: {message.text}")
    msg = bot.reply_to(message, "Сколько отелей вывести?")
    bot.register_next_step_handler(msg, read_hotel_count, search_params=search_params)


def read_hotel_count(message, search_params):
    count = message.text

    if not count.isdigit():
        msg = bot.reply_to(message, "Пожалуйста, введите число отелей цифрой. Сколько отелей вывести?")
        bot.register_next_step_handler(msg, read_hotel_count, search_params=search_params)
        return

    search_params.count = count
    logging.info(f"User: {message.from_user.username}. Search hotel count: {count}")

    msg = bot.reply_to(message, "Введите дату въезда (цифрами, через точку):")
    bot.register_next_step_handler(msg, read_date_arrival, search_params=search_params)


def read_date_arrival(message, search_params):
    arrival = message.text
    date_arrival = arrival.split('.')

    search_params.arrival = date_arrival

    for i in search_params.arrival:
        if not i.isdigit():
            msg = bot.reply_to(message, "Пожалуйста, введите дату въезда цифрой. Какая дата въезда (цифрами, через пробел):")
            bot.register_next_step_handler(msg, read_date_arrival, search_params=search_params)
            return


    if 0 < int(search_params.arrival[0]) > 31 or 0 < int(search_params.arrival[1]) > 12 or 0 < int(search_params.arrival[2]) >= 2025 or int(search_params.arrival[2]) < 2023:
        msg = bot.reply_to(message, "Пожалуйста, введите верный день отъезда. Какая дата отъезда (цифрами, через пробел) :")
        bot.register_next_step_handler(msg, read_date_arrival, search_params=search_params)
        return

    logging.info(f"User: {message.from_user.username}. Recording the arrival date: {date_arrival}")

    msg = bot.reply_to(message, "Введите дату отъезда (цифрами, через точку):")
    bot.register_next_step_handler(msg, read_date_departure, search_params=search_params)

def read_date_departure(message, search_params):
    departure = message.text
    date_departure = (departure.split('.'))

    search_params.departure = date_departure

    for i in search_params.departure:
        if not i.isdigit():
            msg = bot.reply_to(message, "Пожалуйста, введите дату отъезда цифрой. Какая дата отъезда (цифрами, через точку):")
            bot.register_next_step_handler(msg, read_date_departure, search_params=search_params)
            return

    if 0 < int(search_params.departure[0]) > 31 or 0 < int(search_params.departure[1]) > 12 or 0 < int(search_params.departure[2]) >= 2025 or int(search_params.departure[2]) < 2023:
        msg = bot.reply_to(message, "Пожалуйста, введите верный день отъезда. Какая дата отъезда (цифрами, через пробел) :")
        bot.register_next_step_handler(msg, read_date_departure, search_params=search_params)
        return


    if search_params.departure[2] < search_params.arrival[2]:
        bot.send_message(message.from_user.id, "Дата отъезда не может быть раньше даты въезда . Пожалуйста, повторите поиск сначала.")
        return
    elif search_params.departure[2] == search_params.arrival[2] and search_params.departure[1] < search_params.arrival[1]:
        bot.send_message(message.from_user.id, "Дата отъезда не может быть раньше даты въезда . Пожалуйста, повторите поиск сначала.")
        return
    elif search_params.departure[2] == search_params.arrival[2] and search_params.departure[1] == search_params.arrival[1] and search_params.departure[0] < search_params.arrival[0]:
        bot.send_message(message.from_user.id, "Дата отъезда не может быть раньше даты въезда . Пожалуйста, повторите поиск сначала.")
        return


    logging.info(f"User: {message.from_user.username}. Recording the arrival date: {date_departure}")

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


def read_count_photo(message, search_params):
    count_photo = message.text
    logging.info(f"User: {message.from_user.username}. Search hotel count: {count_photo}")

    search_params.count_photo = count_photo
    bot.reply_to(message, "Идет поиск...")
    search_hotel(message, search_params)


def search_hotel(message, search_params):
    logging.info(f"User: {message.from_user.username}. Starting search town coordinates")

    err, coordinates = api.search_coordinates(search_params.country, search_params.town)

    if err or not coordinates:
        logging.error(f"User: {message.from_user.username}. Coordinates for country: '{search_params.country}', "
                      f"town: '{search_params.town}'. Not found")
        bot.send_message(message.from_user.id, "Город или страна не найдены. Пожалуйста, повторите поиск сначала.")
        return
    else:
        logging.info(f"User: {message.from_user.username}. Coordinates successfully found")

    logging.info(f"User: {message.from_user.username}. Starting search hotels")

    err, hotels = api.search_hotels(coordinates, search_params)

    if err or hotels == []:
        logging.error(f"User: {message.from_user.username}. Can't find hotels")
        bot.send_message(message.from_user.id, "Отели не найдены. Пожалуйста, повторите поиск сначала.")
        return


    for hotel in hotels:
        logging.info(f"User: {message.from_user.username}. Checking for the status of the response code")

        data_hotel = api.info_hotels(hotel.id, search_params)

        bot.send_message(message.from_user.id, f"*• Название отеля*:   {hotel.name}. \n\n*• Адрес отеля*:   {data_hotel[0]}. \n\n*• Цена*:   {hotel.price_string}. \n\n*• Диапазон расстояния*:   {hotel.value}.",
                         parse_mode="Markdown")

        logging.info(f"User: {message.from_user.username}. Map search")
        bot.send_photo(message.from_user.id, photo=data_hotel[-1], caption=formatting.mbold("• Местоположение на карте"),
                       parse_mode="MarkdownV2")

        if search_params.show_photo == "Да":
            logging.info(f"User: {message.from_user.username}. Starting search photo")
            lisi_jpeg = []
            bot.send_message(message.from_user.id, f"\n*Фото отеля*:\n", parse_mode="Markdown")
            for i in range(search_params.count_photo):
                lisi_jpeg.append(telebot.types.InputMediaPhoto(data_hotel[1][i]))

            bot.send_media_group(message.from_user.id, lisi_jpeg)


    logging.error(f"User: {message.from_user.username}. Find hotels successfully!")
    bot.send_message(message.from_user.id, f"\n*Поиск закончен!*\n", parse_mode="Markdown")



if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(asctime)s %(levelname)s %(message)s")

    bot.set_my_commands(
        commands=[
            telebot.types.BotCommand("/start", "Start work with bot"),
            telebot.types.BotCommand("/help", "Show help"),
            telebot.types.BotCommand("/lowprice", "Поиск дешевых отелей!"),
            telebot.types.BotCommand("/highprice", "Поиск дорогих отелей!"),
            telebot.types.BotCommand("/bestdeal", "Поиск лучших предложений!")
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
