# app.py
from flask import Flask, render_template
from models import Product
from flask_livereload import LiveReload

app = Flask(__name__)
livereload = LiveReload(app)

# ตัวอย่างรายการอาหาร (ข้อมูลจำลอง)
menu = [
    Product("พิซซ่าหน้าแฮมชีส", 199, "อาหารจานหลัก"),
    Product("สปาเกตตี้คาโบนาร่า", 149, "อาหารจานหลัก"),
    Product("เฟรนช์ฟรายส์", 59, "ของทานเล่น"),
    Product("โค้ก", 29, "เครื่องดื่ม")
]

@app.route('/')
def index():
    return render_template('index.html', menu=menu)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
