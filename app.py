# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
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
        db.session.add(ProductDB(name="พิซซ่าหน้าแฮมชีส", price=199, category="อาหารจานหลัก"))
        db.session.add(ProductDB(name="สปาเกตตี้คาโบนาร่า", price=149, category="อาหารจานหลัก"))
        db.session.add(ProductDB(name="เฟรนช์ฟรายส์", price=59, category="ของทานเล่น"))
        db.session.add(ProductDB(name="โค้ก", price=29, category="เครื่องดื่ม"))
        db.session.commit()

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def index():
    menu = ProductDB.query.all()
    return render_template('index.html', menu=menu)

@app.route('/menu')
def menu_page():
    menu = ProductDB.query.all()
    return render_template('index.html', menu=menu)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Demo login: username=admin, password=1234
        if username == "admin" and password == "1234":
            flash("Login สำเร็จ!", "success")
            return redirect(url_for('index'))
        else:
            flash("Username หรือ Password ไม่ถูกต้อง", "error")

    return render_template('login.html')

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    item = ProductDB.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.price = request.form['price']
        item.category = request.form['category']
        db.session.commit()
        flash("แก้ไขเรียบร้อยแล้ว", "success")
        return redirect(url_for('index'))
    return render_template('edit_item.html', item=item)

@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    item = ProductDB.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("ลบเมนูเรียบร้อยแล้ว", "success")
    return redirect(url_for('index'))


# -----------------------------
# Run server
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

