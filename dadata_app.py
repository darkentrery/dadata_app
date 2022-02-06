from dadata import Dadata
import sqlite3


path_db = "./settings.db"

def set_settings():
    menu = True
    while menu:
        print("Если вы хотите поменять URL введите команду 'URL'")
        print("Если вы хотите поменять API_KEY введите команду 'API_KEY'")
        print("Если вы хотите поменять язык введите команду 'LANGUAGE'")
        print("Если вы хотите поменять вернуться назад введите команду 'BACK'")
        comand = input("Ваша команда: ").lower()
        if comand == 'back':
            menu = False
            continue
        else:
            conn = sqlite3.Connection(path_db)
            cursor = conn.cursor()
            if comand == 'url':
                url = input("Введите желаемый URL: ").lower()
                cursor.execute(f"UPDATE settings SET url = '{url}'")
            elif comand == 'api_key':
                api_key = input("Введите желаемый API_KEY: ").lower()
                cursor.execute(f"UPDATE settings SET api_key = '{api_key}'")
            elif comand == 'language':
                language = input("Введите желаемый LANGUAGE 'ru/en': ").lower()
                if language == 'ru' or language == 'en':
                    cursor.execute(f"UPDATE settings SET language = '{language}'")
                else:
                    print("Вы ввели неверную команду попробуйте еще раз")
            else:
                print("Вы ввели неверную команду попробуйте еще раз")
            conn.commit()
            conn.close()

def get_settings():
    conn = sqlite3.Connection(path_db)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS settings(
    url TEXT,
    api_key TEXT,
    language TEXT
    );""")
    cursor.execute("SELECT * FROM settings")
    if not cursor.fetchall():
        cursor.execute("INSERT INTO settings VALUES (?, ?, ?)", ("https://dadata.ru/", None, 'ru'))
        conn.commit()
    cursor.execute("SELECT * FROM settings")
    settings = cursor.fetchall()
    conn.close()
    return settings[0]

def get_addresses(text, settings):
    if settings[1] is None:
        print("Настройте API_KEY")
        return None
    else:
        with Dadata(settings[1]) as dadata:
            addresses = dadata.suggest(name="address", query=text, language=settings[2], count=20)
        return addresses

def choice(addresses, settings):
    if addresses:
        for n, ad in enumerate(addresses):
            print(f"{n + 1}: {ad['unrestricted_value']}")
        num = int(input("Введите номер соответствующий интересующему вас адресу: ")) - 1
        address = addresses[num]["unrestricted_value"]
        with Dadata(settings[1]) as dadata:
            address = dadata.suggest(name="address", query=address, count=1)
        coordinates = address[0]["data"]["geo_lat"], address[0]["data"]["geo_lon"]
        if coordinates[0] is not None and coordinates[1] is not None:
            coordinates = float(coordinates[0]), float(coordinates[1])
        print(f"Искомые координаты: {coordinates}")
    else:
        print("Адрес не найден. Попробуйте снова.")

def main():
    start = True
    while start:
        settings = get_settings()
        print(f"Чтобы узнать координаты введите адрес.")
        print(f"Для выхода из приложения введите 'exit'")
        print(f"Для изменения настроек введите 'set_settings'")
        print(f"Чтобы узнать текущие настройки введите 'get_settings'")
        text = input("Ввод: ")
        if text == 'exit':
            start = False
            continue
        if text == 'set_settings':
            set_settings()
            start = True
            continue
        if text == 'get_settings':
            settings = get_settings()
            print(f"URL: {settings[0]}, API_KEY: {settings[1]}, LANGUAGE: {settings[2]}")
            start = True
            continue
        addresses = get_addresses(text, settings)
        if addresses is not None:
            choice(addresses, settings)
            start = True

    else:
        print("Спасибо за использование приложения.")

main()

