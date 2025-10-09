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

# -----------------------------
# Order System Models (ใหม่)
# -----------------------------
class OrderDB(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)  # โต๊ะที่ลูกค้านั่ง
    total_price = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')   # active = กำลังสั่ง, paid = ชำระเงินแล้ว

    # Relationship (Composition): 1 order มีหลาย OrderItem
    items = db.relationship('OrderItemDB', backref='order', cascade="all, delete")

    def calc_total(self):
        """คำนวณราคารวมจากทุก OrderItem"""
        self.total_price = sum(item.subtotal() for item in self.items)
        return self.total_price

    def __repr__(self):
        return f"<Order โต๊ะ {self.table_number} - {self.status}>"


class OrderItemDB(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product_db.id'))
    quantity = db.Column(db.Integer, default=1)

    # Relationship: เชื่อมกับ ProductDB
    product = db.relationship('ProductDB')

    def subtotal(self):
        """คำนวณราคารวมต่อรายการ"""
        return self.product.price * self.quantity

    def __repr__(self):
        return f"<Item {self.product.name} x{self.quantity}>"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    items = db.Column(db.String(500), nullable=False)  # เก็บ JSON เช่น {"ผัดไทย": 2, "โค้ก": 1}
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="active")  # active / paid
