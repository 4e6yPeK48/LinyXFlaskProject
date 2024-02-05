import datetime
import json
from urllib.parse import quote_plus

import requests
from flask import Flask, render_template, url_for, redirect, flash, request, jsonify
from flask_login import UserMixin, logout_user, login_required, login_user, current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from forms.login import LoginForm, ChangePasswordForm

# TODO: from werkzeug.security import check_password_hash

csrf = CSRFProtect()
password = 'SbDwFqC@+iD5erM7QAYHE@Jo'
encoded_password = quote_plus(password)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'LinyX_secret_key'
app.config['FLASK_DEBUG'] = 1
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'mysql+mysqlconnector://u11944_HjaF3FL0R2:{encoded_password}@d4.aurorix.net:3306/s11944_anarchy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
EASYDONATE_KEY = '3db0d5db2d1b5ac794aa3e6edca6a414'
app.app_context().push()

db = SQLAlchemy(app)
logmanager = LoginManager()
logmanager.init_app(app)


class Player(UserMixin, db.Model):
    __tablename__ = 'players'
    id = Column(Integer, autoincrement=True, primary_key=True, default=0)
    uuid = Column(String(36), nullable=False, unique=True, default='none')
    name = Column(String, nullable=False, unique=True, default='none')
    ip = Column(String(255))

    password = relationship('Password', back_populates='player')
    purchases = relationship('Purchase', back_populates='player')


class Password(db.Model):
    __tablename__ = 'passwords'
    id = Column(Integer, autoincrement=True, primary_key=True, default=0)
    player_name = Column(String, ForeignKey('players.name'), unique=True, nullable=False)
    password = Column(String, nullable=False, default='none')

    player = relationship('Player', back_populates='password')


class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = Column(Integer, autoincrement=True, primary_key=True, default=0)
    player_name = Column(String, ForeignKey('players.name'), nullable=False, default='none')
    donation_name = Column(String, nullable=False, default='none')
    purchase_date = Column(DateTime(timezone=True), server_default=func.now())

    player = relationship('Player', back_populates='purchases')


def easydonate_get_shop_info():
    easydonate_url = 'https://easydonate.ru/api/v3/shop'

    headers = {'Shop-key': EASYDONATE_KEY}

    response = requests.get(easydonate_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def easydonate_get_products():
    easydonate_url = 'https://easydonate.ru/api/v3/shop/products'
    headers = {'Shop-key': EASYDONATE_KEY}

    response = requests.get(easydonate_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None


@app.route('/')
def index():
    shop_info = easydonate_get_shop_info()
    products_info = easydonate_get_products()

    if shop_info and products_info:
        return render_template('index.html', shop_info=shop_info, products_info=products_info, current_page='index')
    else:
        flash('Ошибка при получении информации о магазине или товарах', 'error')
        return render_template('index.html')


@app.route('/products')
def products():
    shop_info = easydonate_get_shop_info()
    products_info = easydonate_get_products()
    print(products_info)
    if shop_info and products_info:
        return render_template('products.html', shop_info=shop_info, products_info=products_info)
    else:
        flash('Ошибка при получении информации о магазине или товарах', 'error')
        return render_template('index.html')


def easydonate_get_product(product_id):
    easydonate_url = f'https://easydonate.ru/api/v3/shop/product/{product_id}'
    headers = {'Shop-key': EASYDONATE_KEY}

    response = requests.get(easydonate_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None


@app.route('/buy_product/<int:product_id>', methods=['POST'])
def buy_product(product_id):
    product_info = easydonate_get_product(product_id)

    if product_info:
        customer = current_user.name if current_user.is_authenticated else 'Anonymous'
        payment_info = easydonate_create_payment(customer, product_info['response']['servers'][0]['id'],
                                                 {product_id: 1})

        if payment_info and payment_info.get('success'):
            return jsonify({'success': True, 'payment_url': payment_info['response']['url']})
        else:
            return jsonify({'error': 'Ошибка при создании платежа'}), 500
    else:
        return jsonify({'error': 'Ошибка при получении информации о товаре'}), 500


@app.route('/product_info/<int:product_id>')
def product_info(product_id):
    product_info = easydonate_get_product(product_id)

    if product_info:
        return jsonify(product_info)
    else:
        return jsonify({'error': 'Ошибка при получении информации о товаре'}), 500


@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_detail(product_id):
    product_info = easydonate_get_product(product_id)

    if product_info:
        if request.method == 'POST':
            customer = current_user.name if current_user.is_authenticated else 'Anonymous'
            payment_info = easydonate_create_payment(customer, product_info['response']['servers'][0]['id'],
                                                     {product_id: 1})

            if payment_info and payment_info.get('success'):
                payment_url = payment_info['response']['url']
                return f'<script>window.top.location.href = "{payment_url}";</script>'
            else:
                flash('Ошибка при создании платежа', 'error')
                return abort(500)

        print(datetime.datetime.now())
        return render_template('product_detail.html', product_info=product_info, date=datetime.datetime.now())
    else:
        flash('Ошибка при получении информации о товаре', 'error')
        return redirect(url_for('index'))


def easydonate_get_product_info(product_id):
    easydonate_url = f'https://easydonate.ru/api/v3/shop/product/{product_id}'
    headers = {'Shop-key': EASYDONATE_KEY}

    response = requests.get(easydonate_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def easydonate_create_payment(customer, server_id, products, email=None, coupon=None, success_url=None):
    easydonate_url = 'https://easydonate.ru/api/v3/shop/payment/create'
    headers = {'Shop-Key': EASYDONATE_KEY}

    product_id = list(products.keys())[0]
    product_info = easydonate_get_product_info(product_id)

    if not product_info:
        print(f'Ошибка при получении информации о товаре {product_id}')
        return None

    payload = {
        'customer': customer,
        'server_id': server_id,
        'products': json.dumps(products),
        'email': email,
        'coupon': coupon,
        'success_url': success_url,
    }

    try:
        response = requests.get(easydonate_url, params=payload, headers=headers)
        response.raise_for_status()

        response_data = response.json()

        if response_data.get('success'):
            purchase = Purchase(
                player_name=customer,
                donation_name=product_info['response']['name'],
            )
            db.session.add(purchase)
            db.session.commit()
            return response_data
        else:
            print(f'Ошибка при создании платежа: {response_data.get("error_message")}')
            return None
    except requests.exceptions.RequestException as error:
        print(f'Произошла ошибка в запросе: {error}')
        return None
    except ValueError as error:
        print(f'Ошибка при разборе JSON: {error}')
        return None


@logmanager.user_loader
def load_user(user_id):
    return Player.query.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        player_name = form.name.data
        entered_password = form.password.data
        player = Player.query.filter_by(name=player_name).first()

        if player:
            password_entry = Password.query.filter_by(player_name=player_name).first().password
            if password_entry == entered_password:
                login_user(player, remember=form.remember_me.data)
                flash('Вы успешно вошли в аккаунт.', 'success')
                return redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из аккаунта.', 'success')
    return redirect(url_for('index'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    purchases = Purchase.query.filter_by(player_name=current_user.name).all()
    form = ChangePasswordForm()

    if form.validate_on_submit():
        player = Player.query.filter_by(name=current_user.name).first()

        if player.password[0].password == form.current_password.data:
            player.password[0].password = form.new_password.data
            db.session.commit()
            flash('Пароль успешно изменен.', 'success')
            return redirect(url_for('account'))
        else:
            flash('Неверный текущий пароль.', 'error')

    return render_template('account.html', purchases=purchases, form=form)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
