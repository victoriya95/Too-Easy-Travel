import telebot
from telebot import types

import api

bot = telebot.TeleBot('6095050306:AAEsvO8Vdvb69Pc5w9v2rcT2gBh66l4c_I0')


class SearchParams:
    def __init__(self, town):
        self.town = town
        self.country = None
        self.count = None
        self.show_photo = None


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start', 'lowprice'])
def send_welcome(message):
    if message.text in ["/start", "/help"]:
        bot.reply_to(message, "Hi there, I am EchoBot.\n"
                              "I am here to echo your kind words back to you.\n"
                              "Just say anything nice and I'll say the exact same thing to you!")
    elif message.text == "/lowprice":
        msg = bot.reply_to(message, "Пожалуйста введите город, где будем искать отель")
        bot.register_next_step_handler(msg, read_town)
    else:
        bot.send_message(message.from_user.id, "Unknown message")

def read_town(message):
    search_params = SearchParams(message.text)
    # search_params = message.text

    msg = bot.reply_to(message, "В какой стране находится город?")
    bot.register_next_step_handler(msg, read_country, search_params=search_params)


def read_country(message, search_params):
    country = message.text

    msg = bot.reply_to(message, "Сколько отелей вывести?")
    search_params.country = country
    bot.register_next_step_handler(msg, read_hotel_count, search_params=search_params)


def read_hotel_count(message, search_params):
    count = message.text

    if not count.isdigit():
        msg = bot.reply_to(message, "Пожалуйста, введите число отелей цифрой. Сколько отелей вывести?")
        bot.register_next_step_handler(msg, read_hotel_count, search_params=search_params)
        return

    search_params.count = count

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

    search_params.show_photo = photo

    bot.reply_to(message, "Идет поиск...")
    search_hotel(message, search_params)


def search_hotel(message, search_params):
    region_id = api.search_region_id(search_params.town, search_params.country)

    # TODO: check it!
    if region_id == []:
        bot.send_message(message.from_user.id, f"Город не найден. Пожалуйста, повторите поиск сначала.")
        return


    hotels = api.search_hotels(region_id[0], region_id[1], search_params)


    for hotel in hotels:
        bot.send_message(message.from_user.id, f"Название отеля: {hotel.name}, цена: {hotel.price}")
        if search_params.show_photo == "Да":
            bot.send_photo(message.from_user.id, hotel.photo)


if __name__ == "__main__":
    bot.set_my_commands(
        commands=[
            telebot.types.BotCommand("/start", "Start work with bot"),
            telebot.types.BotCommand("/help", "Show help"),
            telebot.types.BotCommand("/lowprice", "Поиск дешевых отелей!")
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
