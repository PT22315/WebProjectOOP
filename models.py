# models.py

from abc import ABC, abstractmethod
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# -----------------------------
# Database Model
# -----------------------------
class ProductDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)

    def get_info(self):
        return f"{self.name} ({self.category}) - {self.price} บาท"

# -----------------------------
# OOP / Business Logic
# -----------------------------
class Item(ABC):
    @abstractmethod
    def get_info(self):
        pass

class Product(Item):
    def __init__(self, name, price, category):
        self.__name = name       # Encapsulation
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

class Menu:
    def __init__(self):
        self.items = []

    def add_item(self, product):
        self.items.append(product)

    def get_menu_info(self):
        return [item.get_info() for item in self.items]


# Example of Polymorphism: Beverage subclass
class Beverage(Product):
    def __init__(self, name, price, size="Medium"):
        super().__init__(name, price, "เครื่องดื่ม")  # Inheritance + Constructor
        self.__size = size  # Encapsulation

    # Polymorphism: override get_info
    def get_info(self):
        return f"{self.get_name()} ({self.__size}) - {self.get_price()} บาท"
