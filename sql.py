import sqlite3


def init_db():
    con, cur = connect()
    create_table(cur)
    con.close()


def connect():
    con = sqlite3.connect("telebot.db")
    cur = con.cursor()
    return con, cur


def create_table(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS users"
                   "(id integer constraint id primary key, username TEXT, command TEXT, date datetime);")

    cursor.execute("CREATE TABLE IF NOT EXISTS history(id integer constraint id references users, name TEXT);")


def search_history(cursor, user_id):
    cursor.execute(f"SELECT id, date, command FROM users WHERE username == '{user_id}' ORDER BY ID DESC LIMIT 1")
    user_info = cursor.fetchone()
    name_id = user_info[0]
    command_time = user_info[1]
    command = user_info[2]

    cursor.execute(f"SELECT name FROM 'history' WHERE id == '{name_id}';")

    hotels = cursor.fetchall()

    list_hotels = []
    for hotel in hotels:
        list_hotels.append(hotel[0])

    return list_hotels, command, command_time


def write_history(connection, cursor, user_id, name_user, command, time, hotels):
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (user_id, name_user, command, time))

    for hotel in hotels:
        cursor.execute("INSERT INTO history VALUES (?, ?)", (user_id, hotel.name))

    connection.commit()
    cursor.close()
