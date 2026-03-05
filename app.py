import re
import requests
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Selenium imports cho các trang khó cào
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sentinel-pro-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sentinel_v4.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODELS ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    # Quan hệ với bảng lịch sử giá
    history = db.relationship('PriceHistory', backref='product', lazy=True, cascade="all, delete-orphan")

    @property
    def latest_price(self):
        last_entry = PriceHistory.query.filter_by(product_id=self.id).order_by(PriceHistory.timestamp.desc()).first()
        return last_entry.price if last_entry else 0

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

# --- ENGINE 1: SHOPEE API (Tốc độ ánh sáng) ---
def get_shopee_price(url):
    try:
        # Tách shopid và itemid từ URL Shopee
        match = re.search(r'i\.(\d+)\.(\d+)', url)
        if not match: return None
        
        shopid, itemid = match.group(1), match.group(2)
        api_url = f"https://shopee.vn/api/v4/item/get?itemid={itemid}&shopid={shopid}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://shopee.vn/"
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Giá Shopee lưu trong hệ thống thường nhân với 100,000
            raw_price = data.get("data", {}).get("item", {}).get("price")
            return int(raw_price / 100000) if raw_price else None
    except Exception as e:
        print(f"Shopee API Error: {e}")
    return None

# --- ENGINE 2: SELENIUM (Dành cho Haravan/Sapo/Web khác) ---
def get_selenium_price(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # Tắt load ảnh để chạy nhanh
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        # Các selector phổ biến cho shop VN (XIXEOSHOP, Thế giới di động, v.v.)
        selectors = [".pro-price", ".current-price", ".product-price", ".price", "#price-preview"]
        for s in selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, s)
                if element.text:
                    # Làm sạch chuỗi giá
                    clean_price = "".join(filter(str.isdigit, element.text))
                    if clean_price: return int(clean_price)
            except: continue
    finally:
        driver.quit()
    return None

# --- MAIN DISPATCHER (Bộ điều phối) ---
def fetch_price(url):
    if "shopee.vn" in url:
        return get_shopee_price(url)
    return get_selenium_price(url)

# --- ROUTES ---
@app.template_filter('vnd')
def format_vnd(value):
    if not value or value == 0: return "N/A"
    return "{:,.0f} đ".format(value).replace(",", ".")

@app.route('/')
def index():
    products = Product.query.all()
    # Sắp xếp lịch sử giá tăng dần theo thời gian để vẽ biểu đồ
    for p in products:
        p.ordered_history = PriceHistory.query.filter_by(product_id=p.id).order_by(PriceHistory.timestamp.asc()).all()
    return render_template('index.html', products=products)

@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    url = request.form.get('url')
    if name and url:
        new_prod = Product(name=name, url=url)
        db.session.add(new_prod)
        db.session.commit()
        
        # Quét giá lần đầu ngay lập tức
        price = fetch_price(url)
        if price:
            db.session.add(PriceHistory(price=price, product_id=new_prod.id))
            db.session.commit()
    return redirect(url_for('index'))

@app.route('/scan')
def scan():
    products = Product.query.all()
    for p in products:
        price = fetch_price(p.url)
        if price:
            db.session.add(PriceHistory(price=price, product_id=p.id))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    prod = Product.query.get(id)
    if prod:
        db.session.delete(prod)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)