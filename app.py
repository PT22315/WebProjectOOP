# app.py
from flask import Flask, render_template, request, redirect, url_for, flash ,session
from models import db, ProductDB
from flask_livereload import LiveReload

app = Flask(__name__)
livereload = LiveReload(app)

# ต้องมี secret_key สำหรับ flash message
app.secret_key = "your_secret_key"

# -----------------------------
# Database config
# -----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

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
            image_url=None  # ไม่มีรูปก็ได้
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
# Routes
# -----------------------------
@app.route('/')
def index():
    menu = ProductDB.query.all()
    cart_count = session.get("cart_count", 0)
    total_price = session.get("total_price", 0.00)
    return render_template('index.html', menu=menu, cart_count=cart_count, total_price=total_price)

@app.route('/menu_page')
def menu_page():
    menu = ProductDB.query.all()
    cart_count = session.get("cart_count", 0)
    total_price = session.get("total_price", 0.00)
    return render_template('index.html', menu=menu, cart_count=cart_count, total_price=total_price)

# =========================
# Login Route
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["user"] = username  # เก็บ user ใน session
            flash("เข้าสู่ระบบสำเร็จ!", "success")
            return redirect(url_for("index"))
        else:
            flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "error")
            return redirect(url_for("login"))
        
    # ส่งค่า cart summary ไปด้วย (กัน error header)
    cart_count = session.get("cart_count", 0)
    total_price = session.get("total_price", 0.00)
    return render_template("login.html", cart_count=cart_count, total_price=total_price)

@app.route("/logout")
def logout():
    session.pop("user", None)  # ลบ user ออกจาก session
    flash("ออกจากระบบเรียบร้อยแล้ว", "success")
    return redirect(url_for("index"))


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    item = ProductDB.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.price = request.form['price']
        item.image_url = request.form.get('image_url') 
        db.session.commit()
        flash('อัปเดตเมนูเรียบร้อยแล้ว', 'success')
        return redirect(url_for('index'))
    return render_template('edit_item.html', item=item)


@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    item = ProductDB.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("ลบเมนูเรียบร้อยแล้ว", "success")
    return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        category = request.form['category']
        image_url = request.form.get('image_url')  # optional

        new_item = ProductDB(
            name=name,
            price=price,
            category=category,
            image_url=image_url
        )
        db.session.add(new_item)
        db.session.commit()
        flash('เพิ่มสินค้าเรียบร้อยแล้ว', 'success')
        return redirect(url_for('index'))

    return render_template('add_item.html')
# -----------------------------
# Run server
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

