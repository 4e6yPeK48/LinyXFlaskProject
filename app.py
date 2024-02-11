import json
import threading
from urllib.parse import quote_plus
from functools import lru_cache
import argparse
from ProtocolClient.client import MessagingChannelHandler
from ProtocolClient.Types.PacketType import PacketType
import requests
from flask import Flask, render_template, url_for, redirect, flash, jsonify, request
from flask_login import UserMixin, logout_user, login_required, login_user, current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from jinja2.exceptions import TemplateNotFound, UndefinedError
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.exc import OperationalError, IntegrityError, PendingRollbackError
from sqlalchemy.orm import relationship
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden, MethodNotAllowed, InternalServerError, \
    ServiceUnavailable, RequestTimeout, NotFound

from forms.login import LoginForm, ChangePasswordForm

# TODO: добавить последние покупки

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

handled = dict[str, tuple[bool, str]]

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
    """Возвращает json для информации о магазине"""

    easydonate_url = 'https://easydonate.ru/api/v3/shop'

    headers = {'Shop-key': EASYDONATE_KEY}

    response = requests.get(easydonate_url, headers=headers)
    print('easydonate_get_shop_info')

    if response.status_code == 200:
        return response.json()
    else:
        return None


@lru_cache(maxsize=None)
def easydonate_get_products_cached():
    """Возвращает json с информацией о всех товарах магазина"""
    easydonate_url = 'https://easydonate.ru/api/v3/shop/products'
    headers = {'Shop-key': EASYDONATE_KEY}

    response = requests.get(easydonate_url, headers=headers)
    print('easydonate_get_products_cached')

    if response.status_code == 200:
        return response.json()
    else:
        return None


def preload_product_descriptions():
    """Предзагружает описание товаров"""

    products_info = easydonate_get_products_cached()

    if products_info:
        product_ids = [product['id'] for product in products_info.get('response', [])]

        def send_product_request(product_id):
            easydonate_get_product(product_id)

        def send_requests_periodically():
            for product_id in product_ids:
                send_product_request(product_id)
                threading.Event().wait(1)  # 0.5 секунды

        thread = threading.Thread(target=send_requests_periodically)
        thread.start()


def easydonate_get_products():
    return easydonate_get_products_cached()


def easydonate_create_payment(customer, server_id, items, email=None, coupon=None, success_url=None):
    """Создание платежа для магазина"""

    easydonate_url = 'https://easydonate.ru/api/v3/shop/payment/create'
    headers = {'Shop-Key': EASYDONATE_KEY}

    # product_id = list(items.keys())[0]
    # product_info = easydonate_get_product(product_id)

    # if not product_info:
    #     print(f'Ошибка при получении информации о товаре {product_id}')
    #     return None

    payload = {
        'customer': customer,
        'server_id': server_id,
        'products': json.dumps(items),
        'email': email,
        'coupon': coupon,
        'success_url': success_url,
    }

    try:
        response = requests.get(easydonate_url, params=payload, headers=headers)
        print('easydonate_create_payment')
        response.raise_for_status()

        response_data = response.json()

        if response_data.get('success'):
            # purchase = Purchase(
            #     player_name=customer,
            #     donation_name=product_info['response']['name'],
            # )
            # db.session.add(purchase)
            # db.session.commit()
            return response_data
        else:
            print(f'Ошибка при создании платежа: {response_data}')
            return None
    except requests.exceptions.RequestException as error:
        print(f'Произошла ошибка в запросе: {error}')
        return None
    except ValueError as error:
        print(f'Ошибка при разборе JSON: {error}')
        return None


@lru_cache(maxsize=None)
def easydonate_get_product(product_id):
    """Возвращает json с информацией о товаре магазина"""
    easydonate_url = f'https://easydonate.ru/api/v3/shop/product/{product_id}'
    headers = {'Shop-key': EASYDONATE_KEY}

    response = requests.get(easydonate_url, headers=headers)
    print(f'easydonate_get_product({product_id})')

    if response.status_code == 200:
        return response.json()
    else:
        return None


@app.route('/')
def index():
    products_info = easydonate_get_products()

    if products_info:
        return render_template('index.html', products_info=products_info, current_page='index')
    else:
        flash('Ошибка при получении информации о магазине или товарах', 'error')
        return render_template('index.html')


@app.route('/products')
def products():
    products_info = easydonate_get_products()
    if products_info:
        return render_template('products.html', products_info=products_info)
    else:
        flash('Ошибка при получении информации о магазине или товарах', 'error')
        return render_template('index.html')


@app.route('/product_info/<int:product_id>')
def product_info_json(product_id):
    product_info = easydonate_get_product(product_id)

    if product_info:
        return jsonify(product_info)
    else:
        return jsonify({'error': 'Ошибка при получении информации о товаре'}), 500


@app.route('/buy_product/<int:product_id>', methods=['POST'])
def buy_product(product_id):
    customer = current_user.name if current_user.is_authenticated else 'Anonymous'
    payment_info = easydonate_create_payment(customer, '79936', {product_id: 1})

    if payment_info and payment_info.get('success'):
        return jsonify({'success': True, 'payment_url': payment_info['response']['url']})
    else:
        return jsonify({'error': 'Ошибка при создании платежа'}), 500


parser = argparse.ArgumentParser()

parser.add_argument('--host', type=str, default="localhost")
parser.add_argument('--port', type=int, default=12345)
parser.add_argument('--debug', type=bool, default=False)
parser.add_argument('--passw', type=str, default="?thisIsPassword?")
parser.add_argument('--forceProtocol', type=str, default=PacketType.PROTOCOL_VERSION)

args = parser.parse_args()


# Определение обработчика ответа на двухфакторную аутентификацию
def fa_response_handler(packet: dict, client: MessagingChannelHandler) -> None:
    if args.debug:
        print(f'Received response from server {packet}')

    if packet["status"] == PacketType.SUCCESS:
        handled[packet["nickname"]] = (True, packet["reason"])
    else:
        if args.debug:
            print(f'Denied 2FA from nickname {packet["nickname"]} for reason {packet["reason"]}')
            handled[packet["nickname"]] = (False, packet["reason"])


messagingChannel: MessagingChannelHandler = MessagingChannelHandler(
    address=(args.host, args.port), side=PacketType.SITESIDE,
    isDebug=args.debug
)

messagingChannel.registrateExecutor(fa_response_handler, PacketType.SITESIDE_2FA_RESPONSE)
messagingChannel.start(args.passw, args.forceProtocol)


def send_packet(packet: dict) -> None:
    messagingChannel.sendPacket(packet=packet)


# sendPacket(PacketType.get_BOTSIDE_2FA_NEEDED('overdrive1')) # 'overdrive1' - nickname


def _containsAll (data, values):
    try:
        return all(key in data for key in values)
    except TypeError as e:
        print ("Generated TypeError: "+str(e)+" from data "+str(data)+" and values "+str(values))


@app.route('/confirm_login', methods=['POST'])
def confirm_login(nickname):

    if _containsAll(handled, [nickname]):
        is_authed, reason = handled[nickname]
        if is_authed:
            return redirect(url_for("index"))  # authed
        else:
            return jsonify({"error": f"Отказано по причине {reason}"})


@logmanager.user_loader
def load_user(user_id):
    return db.session.get(Player, user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        nickname = form.name.data
        send_packet(PacketType.get_BOTSIDE_2FA_NEEDED(nickname))
        # Передаем никнейм в функцию confirm_login
        confirm_login(nickname)
        return redirect(url_for('index'))  # Перенаправляем на главную страницу

    return render_template('login.html', form=form)

    # if form.validate_on_submit():
    #     player_name = form.name.data
    #     # entered_password = form.password.data
    #     player = Player.query.filter_by(name=player_name).first()
    #
    #     if player:
    #         # password_entry = Password.query.filter_by(player_name=player_name).first().password
    #         # if password_entry == entered_password:
    #         if True:
    #             login_user(player, remember=form.remember_me.data)
    #             flash('Вы успешно вошли в аккаунт. Новый', 'success')
    #             return redirect(url_for('index'))
    #     flash('Нет такого игрока.', 'success')
    # return render_template('login.html', form=form)


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


@app.errorhandler(OperationalError)
def handle_operational_error():
    return render_template('error.html',
                           message="Произошла операционная ошибка. "
                                   "Пожалуйста, обновите страницу или свяжитесь с нами."), 500


@app.errorhandler(IntegrityError)
def handle_integrity_error():
    return render_template('error.html',
                           message="Произошла ошибка целостности данных. "
                                   "Пожалуйста, обновите страницу или свяжитесь с нами."), 500


@app.errorhandler(NotFound)
def handle_not_found_error():
    return render_template('error.html',
                           message="Страница не найдена. "
                                   "Пожалуйста, проверьте правильность URL или свяжитесь с нами."), 404


@app.errorhandler(BadRequest)
def handle_bad_request():
    return render_template('error.html',
                           message="Неправильный запрос. "
                                   "Пожалуйста, проверьте правильность отправленных данных."), 400


@app.errorhandler(Unauthorized)
def handle_unauthorized():
    return render_template('error.html', message="Для доступа к этому ресурсу требуется авторизация."), 401


@app.errorhandler(Forbidden)
def handle_forbidden():
    return render_template('error.html', message="У вас нет доступа к этому ресурсу."), 403


@app.errorhandler(MethodNotAllowed)
def handle_method_not_allowed():
    return render_template('error.html', message="Метод HTTP не поддерживается для этого ресурса."), 405


@app.errorhandler(InternalServerError)
def handle_internal_server_error():
    return render_template('error.html', message="Внутренняя ошибка сервера. "
                                                 "Пожалуйста, попробуйте позже."), 500


@app.errorhandler(PendingRollbackError)
def handle_pending_rollback_error():
    return render_template('error.html', message="Внутренняя ошибка сервера. "
                                                 "Пожалуйста, попробуйте позже."), 500


@app.errorhandler(ServiceUnavailable)
def handle_service_unavailable():
    return render_template('error.html', message="Сервис временно недоступен. "
                                                 "Пожалуйста, попробуйте позже."), 503


@app.errorhandler(RequestTimeout)
def handle_request_timeout():
    return render_template('error.html',
                           message="Время ожидания запроса истекло. "
                                   "Пожалуйста, попробуйте позже."), 504


@app.errorhandler(TemplateNotFound)
def handle_template_not_found():
    return "Шаблон не найден. Пожалуйста, свяжитесь с администратором сайта.", 404


@app.errorhandler(UndefinedError)
def handle_undefined_error():
    return render_template('error.html',
                           message="Неизвестная ошибка. "
                                   "Пожалуйста, свяжитесь с администратором сайта."), 404


@app.errorhandler(404)
def not_found_error():
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error():
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    import os

    os.environ['FLASK_ENV'] = 'production'
    db.create_all()
    preload_product_descriptions()

    from waitress import serve

    # serve(app, host='localhost', port=5000)
    serve(app, host='46.174.48.78', port=5000)

# if __name__ == '__main__':
#     db.create_all()
#     app.run(debug=True)
