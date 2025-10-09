# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, ProductDB, OrderDB, OrderItemDB
from flask_livereload import LiveReload
import os
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
livereload = LiveReload(app)

app.secret_key = "your_secret_key"

# -----------------------------
# Database config
# -----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# -----------------------------
# Upload folder
# -----------------------------
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# -----------------------------
# สร้างตารางและสินค้าเริ่มต้น
# -----------------------------
with app.app_context():
    db.create_all()
    if not ProductDB.query.first():
        db.session.add(ProductDB(
            name="พิซซ่าหน้าแฮมชีส", price=199, category="อาหารจานหลัก",
            image_url="https://cdn.pizzahut.co.th/pizzas-by-size/ham-and-cheese_hce-vertical-M-08022024104537.jpg"
        ))
        db.session.add(ProductDB(
            name="สปาเกตตี้คาโบนาร่า", price=149, category="อาหารจานหลัก",
            image_url=None
        ))
        db.session.add(ProductDB(
            name="เฟรนช์ฟรายส์", price=59, category="ของทานเล่น",
            image_url=None
        ))
        db.session.add(ProductDB(
            name="โค้ก", price=29, category="เครื่องดื่ม",
            image_url=None
        ))
        db.session.commit()

# -----------------------------
# หน้าเมนู / Home
# -----------------------------
@app.route('/')
def index():
    menu = ProductDB.query.all()
    cart = session.get('cart', {})
    cart_count = sum(cart.values())
    total_price = sum(ProductDB.query.filter_by(name=name).first().price * qty for name, qty in cart.items() if ProductDB.query.filter_by(name=name).first())
    return render_template('index.html', menu=menu, cart_count=cart_count, total_price=total_price)

@app.route('/menu_page')
def menu_page():
    return redirect(url_for('index'))

# -----------------------------
# Login / Logout
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "1234":
            session["user"] = username
            flash("เข้าสู่ระบบสำเร็จ!", "success")
            return redirect(url_for("index"))
        else:
            flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "error")
            return redirect(url_for("login"))
    cart = session.get('cart', {})
    return render_template("login.html", cart_count=sum(cart.values()), total_price=0)

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("table_number", None)
    session.pop("cart", None)
    flash("ออกจากระบบเรียบร้อยแล้ว", "success")
    return redirect(url_for('index'))

# -----------------------------
# Table Selection
# -----------------------------
@app.route("/select_table")
def select_table():
    return render_template("select_table.html")

@app.route("/set_table/<int:number>")
def set_table(number):
    session["table_number"] = number
    flash(f"เลือกโต๊ะ {number} แล้ว", "success")
    return redirect(url_for("index"))

# -----------------------------
# Add / Edit / Delete Menu Items
# -----------------------------
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        category = request.form.get('category', '')
        file = request.files.get('image_file')
        image_url = ''
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = url_for('static', filename=f'uploads/{filename}')
        db.session.add(ProductDB(name=name, price=price, category=category, image_url=image_url))
        db.session.commit()
        flash('เพิ่มเมนูสำเร็จ!')
        return redirect(url_for('index'))
    return render_template('add_item.html')

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    item = ProductDB.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.price = float(request.form['price'])
        item.image_url = request.form.get('image_url')
        db.session.commit()
        flash("แก้ไขเมนูเรียบร้อยแล้ว")
        return redirect(url_for('index'))
    return render_template('edit_item.html', item=item)

@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    item = ProductDB.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("ลบเมนูเรียบร้อยแล้ว")
    return redirect(url_for('index'))

# -----------------------------
# Cart (Session)
# -----------------------------
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    data = request.json
    name = data['name']
    qty = int(data['qty'])
    if qty <= 0:
        return jsonify({"status":"error", "msg":"จำนวนต้องมากกว่า 0"})
    cart = session.get('cart', {})
    cart[name] = cart.get(name, 0) + qty
    session['cart'] = cart
    return jsonify({"status":"success", "cart":cart})

# -----------------------------
# Checkout
# -----------------------------
@app.route("/checkout", methods=["POST"])
def checkout():
    table_number = session.get("table_number")
    if not table_number:
        flash("โปรดเลือกโต๊ะก่อนสั่งอาหาร", "error")
        return redirect(url_for("index"))

    cart_json = request.form.get("cart_data")
    if not cart_json:
        flash("ตะกร้าว่าง", "error")
        return redirect(url_for("index"))

    cart = json.loads(cart_json)
    if not cart:
        flash("ตะกร้าว่าง", "error")
        return redirect(url_for("index"))

    # ตรวจสอบว่ามี Active Order อยู่แล้วหรือยัง
    order = OrderDB.query.filter_by(table_number=table_number, status="active").first()
    if not order:
        order = OrderDB(table_number=table_number, status="active")
        db.session.add(order)
        db.session.commit()

    # เพิ่มรายการสินค้าเข้า OrderItemDB
    total_price = order.total_price or 0
    for name, info in cart.items():
        product = ProductDB.query.filter_by(name=name).first()
        if product:
            qty = info['qty']
            total_price += product.price * qty
            db.session.add(OrderItemDB(order_id=order.id, product_id=product.id, quantity=qty))
    order.total_price = total_price
    db.session.commit()

    session['cart'] = {}  # เคลียร์ cart
    flash("สั่งอาหารเรียบร้อยแล้ว", "success")
    return redirect(url_for('active_orders'))


# -----------------------------
# Active Orders Page
# -----------------------------
@app.route("/active_orders")
def active_orders():
    orders = OrderDB.query.filter_by(status="active").all()
    return render_template("active_order.html", orders=orders)

# -----------------------------
# ชำระเงิน order
# -----------------------------
@app.route("/pay_order/<int:order_id>", methods=["POST"])
def pay_order(order_id):
    order = OrderDB.query.get_or_404(order_id)
    order.calc_total()  # คำนวณราคารวมก่อนจ่าย
    order.status = "paid"
    db.session.commit()
    flash(f"ชำระเงินโต๊ะ {order.table_number} เรียบร้อยแล้ว", "success")
    return redirect(url_for("active_orders"))

# -----------------------------
# Order History Page
# -----------------------------
@app.route("/history")
def order_history():
    orders = OrderDB.query.filter_by(status="paid").all()
    return render_template("order_history.html", orders=orders)

# -----------------------------
# Clear session
# -----------------------------
@app.route('/clear_session')
def clear_session():
    session.clear()
    return redirect(url_for('index'))

# -----------------------------
# Run server
# -----------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=True)
