from dadata import Dadata
import sqlite3



path_db = "./settings.db"


class Database:
    def __init__(self, path_db):
        self.conn = sqlite3.Connection(path_db)
        self.cursor = self.conn.cursor()
        self.default_settings()

    def default_settings(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS settings(
                    url TEXT,
                    api_key TEXT,
                    language TEXT
                    );""")
        if not self.cursor.fetchall():
            self.cursor.execute("INSERT INTO settings VALUES (?, ?, ?)", ("https://dadata.ru/", None, 'ru'))
            self.conn.commit()

    def get_settings(self):
        self.cursor.execute("SELECT * FROM settings")
        self.settings = self.cursor.fetchall()[0]
        return self.settings

    def set_settings(self, settings):
        url, api_key, language = settings
        if url is not None:
            self.cursor.execute(f"UPDATE settings SET url = '{url}'")
        if api_key is not None:
            self.cursor.execute(f"UPDATE settings SET api_key = '{api_key}'")
        if language is not None:
            self.cursor.execute(f"UPDATE settings SET language = '{language}'")
        self.conn.commit()


class Dadata_class:
    def set_settings(self, settings):
        self.settings = settings

    def first_choice(self, text):
        if self.settings[1] is not None:
            with Dadata(self.settings[1]) as dadata:
                self.addresses = dadata.suggest(name="address", query=text, language=self.settings[2], count=20)

    def second_choice(self, num):
        coordinates = None
        if self.addresses:
            address = self.addresses[num]["unrestricted_value"]
            with Dadata(self.settings[1]) as dadata:
                address = dadata.suggest(name="address", query=address, count=1)
            coordinates = address[0]["data"]["geo_lat"], address[0]["data"]["geo_lon"]
            if coordinates[0] is not None and coordinates[1] is not None:
                coordinates = float(coordinates[0]), float(coordinates[1])
        return coordinates


class Menu:
    def __init__(self):
        self.url = None
        self.api_key = None
        self.language = None
        self.num = None

    def main_menu(self):
        print(f"Чтобы узнать координаты введите адрес.")
        print(f"Для выхода из приложения введите 'exit'")
        print(f"Для изменения настроек введите 'set_settings'")
        print(f"Чтобы узнать текущие настройки введите 'get_settings'")
        self.text = input("Ввод: ")


    def set_settings(self):
        print("Если вы хотите поменять URL введите команду 'URL'")
        print("Если вы хотите поменять API_KEY введите команду 'API_KEY'")
        print("Если вы хотите поменять язык введите команду 'LANGUAGE'")
        print("Если вы хотите поменять вернуться назад введите команду 'BACK'")
        self.comand = input("Ваша команда: ").lower()
        self.set_setting()

    def set_setting(self):
        if self.comand == 'back':
            pass
        elif self.comand == 'url':
            self.url = input("Введите желаемый URL: ").lower()
        elif self.comand == 'api_key':
            self.api_key = input("Введите желаемый API_KEY: ").lower()
        elif self.comand == 'language':
            self.language = input("Введите желаемый LANGUAGE 'ru/en': ").lower()
            if self.language != 'ru' and self.language != 'en':
                self.language = None
                print("Вы ввели неверную команду попробуйте еще раз")
                self.set_settings()
        else:
            print("Вы ввели неверную команду попробуйте еще раз")
            self.set_settings()
        self.settings =  self.url, self.api_key, self.language

    def get_settings(self, settings):
        print(f"URL: {settings[0]}, API_KEY: {settings[1]}, LANGUAGE: {settings[2]}")

    def set_num(self, addresses):
        for n, ad in enumerate(addresses):
            print(f"{n + 1}: {ad['unrestricted_value']}")
        if addresses:
            self.num = int(input("Введите номер соответствующий интересующему вас адресу: ")) - 1
        else:
            print("Адреса не обнаружено")

    def get_coordinates(self, coordinates):
        if coordinates is not None:
            print(f"Искомые координаты: {coordinates}")
        else:
            print("Адрес не найден. Попробуйте снова.")

    def exit(self):
        print("Вы успешно вышли из программы")


class Controler:
    def __init__(self, path_db):
        self.menu = Menu()
        self.data = Database(path_db)
        self.dadata = Dadata_class()


    def start(self):
        self.menu.main_menu()
        self.text = self.menu.text
        if self.text == 'exit':
            self.menu.exit()
        elif self.text == 'set_settings':
            self.menu.set_settings()
            self.data.set_settings(self.menu.settings)
            self.start()
        elif self.text == 'get_settings':
            self.menu.get_settings(self.data.get_settings())
            self.start()
        else:
            self.get_coordinates()

    def get_coordinates(self):
        self.dadata.set_settings(self.data.get_settings())
        self.dadata.first_choice(self.text)
        self.menu.set_num(self.dadata.addresses)
        coordinates = self.dadata.second_choice(self.menu.num)
        self.menu.get_coordinates(coordinates)
        self.start()


c = Controler(path_db)
c.start()