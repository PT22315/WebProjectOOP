# models.py

class Product:
    def __init__(self, name, price, category):
        self.__name = name       # ใช้ encapsulation
        self.__price = price
        self.__category = category

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_category(self):
        return self.__category

    def get_info(self):
        return f"{self.__name} ({self.__category}) - {self.__price} บาท"

