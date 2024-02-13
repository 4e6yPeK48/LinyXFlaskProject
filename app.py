import json
import threading
from urllib.parse import quote_plus
from functools import lru_cache

import requests
from flask import Flask, render_template, url_for, redirect, flash, jsonify, request
from flask_login import UserMixin, logout_user, login_required, current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from jinja2.exceptions import TemplateNotFound, UndefinedError
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.exc import OperationalError, IntegrityError, PendingRollbackError
from sqlalchemy.orm import relationship
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden, MethodNotAllowed, InternalServerError, \
    ServiceUnavailable, RequestTimeout, NotFound

from forms.login import LoginForm, ChangePasswordForm

# Liny start

# For features start
# from flask_login import login_user
# For features end

from concurrent.futures import ThreadPoolExecutor
import argparse
import discord
import asyncio
import datetime
from waitress import serve
import mysql.connector

# Liny end

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
discord_token = 'MTE5ODAxNjU2NTI3NTI3MTE2OA.G1vWTl.TTMeTsKBddR1x4fS9RF5aFrO7JybGMxw9mXixU'
app.app_context().push()

db = SQLAlchemy(app)
logmanager = LoginManager()
logmanager.init_app(app)

# Liny start
table_namespace = ["DISCORD_ID", "SOCIAL", "LOWERCASENICKNAME"]

connection = mysql.connector.connect(
    host="d6.aurorix.net",
    port=3306,
    user="u16757_3kOuywUod7",
    password="GmO!Rv0M+AFy+vBIGMnlQh@7",
    database="s16757_limboauth"
)

if not connection:
    print("Error while connect to MariaDB")
    quit()


def get_current_time() -> float:
    current_time = datetime.datetime.now()
    return (current_time - current_time.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )).total_seconds()


async def get_discord_id(nickname):
    if not connection:
        print("Error while connect to MariaDB")
        quit()
    if not connection.is_connected():
        print("Error while connect to MariaDB")
        quit()
    cursor = connection.cursor()

    cursor.execute(
        f"SELECT {table_namespace[0]} FROM {table_namespace[1]} WHERE {table_namespace[2]} = %s",
        (nickname.lower(),)
    )

    row = cursor.fetchone()
    if row:
        cursor.close()
        return row[0]


for_bot: list[str] = []  # Containing all nickname's of player's to 2fa
for_site: dict[str, tuple[bool, str]] = {}  # Containing 2fa result

client = discord.Client(intents=discord.Intents.all())


async def check_tags():
    while True:
        for _ in range(len(for_bot)):
            last_nickname = for_bot.pop()
            await send_confirmation_ticket(last_nickname)
        await asyncio.sleep(1)


@client.event
async def on_ready() -> None:
    asyncio.create_task(check_tags())
    print('Logged on as', client.user)


@client.event
async def on_message(message) -> None:
    if message.author == client.user:
        return
    if message.content.startswith('$test'):
        await message.channel.send(f'Application working. Len of param for_bot: {len(for_bot)}')


async def send_confirmation_ticket(player: str):
    if not player:
        print("Player can't be None!")

    discord_id = await get_discord_id(player)

    if not discord_id:
        print(f"Can't find discord id for nickname {player}")
        return

    class ConfirmationTicket(discord.ui.View):
        @discord.ui.button(label="Подтвердить", style=discord.ButtonStyle.success,
                           custom_id=str(discord_id) + player + "Accept")
        async def first_button_callback(self, ctx, ignored):
            user_name = ctx.user.name
            if player in for_site.keys():
                denied = discord.Embed(title="Вы уже подтверждали запрос", color=0xe100ff)
                denied.set_footer(text=f"Дейстиве не выполнено, {user_name}!")
                await ctx.response.send_message(embed=denied)  # Already accepted
            else:
                success = discord.Embed(title="Вы подтвердили запрос на вход", color=0xe100ff)
                success.set_footer(text=f"Дейстиве выполнено, {user_name}!")
                for_site[player] = (True, "")
                await ctx.response.send_message(embed=success)  # Accepting

        @discord.ui.button(label="Отклонить", style=discord.ButtonStyle.red,
                           custom_id=str(discord_id) + player + "Denied")
        async def second_button_callback(self, ctx, ignored):
            user_name = ctx.user.name
            if player in for_site.keys():
                denied = discord.Embed(title="Вы уже отклоняли подтверждение входа", color=0xe100ff)
                denied.set_footer(text=f"Дейстиве не выполнено, {user_name}!")
                await ctx.response.send_message(embed=denied)  # Already nope
            else:
                success = discord.Embed(title="Вы отклонили подтверждение входа", color=0xe100ff)
                success.set_footer(text=f"Дейстиве выполнено, {user_name}!")
                for_site[player] = (False, "Discord integration")
                await ctx.response.send_message(embed=success)  # Nope

    confirmation = discord.Embed(title="Подтверждение для входа на сайт", color=0xe100ff)
    confirmation.add_field(
        name="",
        value="Если вы не пытались войти на сайт, пожалуйста, обратите на это " +
              "внимание."
    )
    confirmation.set_footer(text="LinyX Technology Group")

    try:
        user = await client.fetch_user(discord_id)
        await user.send(embed=confirmation, view=ConfirmationTicket())
    except discord.errors.Forbidden:  # Nope
        for_site[player] = (False, "Permission error: Бот не может отправить сообщение этому пользователю. Скорее "
                                   "всего личные сообщения закрыты")
        print("Permission error: Cannot send messages to this user.")
    except discord.errors.NotFound:  # Nope
        for_site[player] = (False, "NotFound error: Пользователя нет на канале LinyX(?), поэтому бот не может "
                                   "отправить ему сообщение.")
        print("User not found on this server.")


# Debug only start
# def get_random_bool():
#     random_number = random.random()
#     if random_number < 0.2:
#         return True
#     else:
#         return False


# def is_complete_user(nickname: str = ""):
#     is_completed = get_random_bool()
#     if is_completed:
#         print(f"Okay, redirecting player {nickname}")
#     else:
#         print(f"Okay, wait more time")
#     return get_random_bool()
# Debug only end


@app.route('/confirm_login', methods=['GET'])
def confirm_login():
    for_bot.append(request.args.get('nickname'))
    print(f"Appending param for_bot, len: {len(for_bot)}")
    return render_template('confirm_login.html', nickname=request.args.get('nickname'))


@app.route('/operation_status', methods=['GET'])
def operation_status():
    if request.args.get('nickname') in for_site.keys():
        is_authed, reason = for_site.pop(request.args.get('nickname'))
        if is_authed:
            return jsonify({'status': 'complete'})
        else:
            return jsonify({'status': 'error', 'error_content': reason})
    else:
        return jsonify({'status': 'processing'})


# Liny end


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
                threading.Event().wait(1)  # 0.5 secs

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


@logmanager.user_loader
def load_user(user_id):
    return db.session.get(Player, user_id)


# Liny start
# @app.route('/confirm_login', methods=['GET'])
# def confirm_login():
#     nickname = request.args.get('nickname')
#     if nickname:
#         if args.debug:
#             print(f'Nickname post: {nickname}')
#         if _containsAll(handled, [nickname]):
#             is_authed, reason = handled[nickname]
#             if args.debug:
#                 print(f'Nickname in dictionary')
#             try:
#                 if is_authed:
#                     if args.debug:
#                         print(f'Nickname authed: {nickname}')
#                     player = Player.query.filter_by(name=nickname).first()
#                     login_user(player)
#                     flash('Вы успешно вошли в аккаунт', 'success')
#                     return redirect(url_for('index'))
#                 else:
#                     if args.debug:
#                         print(f'Not authed by reason : {reason}')
#                     flash(f'Невозможно войти по причине {reason}', 'error')
#                     print(f'handled: {handled}')
#                     return redirect(url_for('login'))
#             finally:
#                 _ = handled.pop(nickname, None)
#         else:
#             if args.debug:
#                 print(f'Waiting containing for player: {nickname}')
#             flash(f'Ожидание подтверждения  игрока {nickname}', 'success')
#             return render_template('confirm_login.html', nickname=nickname)
#     else:
#         if args.debug:
#             print(f'No nickname present')
#         flash(f'Никнейм не предоставлен', 'error')
#         return redirect(url_for('login'))
# Liny end


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        nickname = form.name.data
        # Liny start
        return redirect(url_for('confirm_login', nickname=nickname))
        # Liny end

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
    parser = argparse.ArgumentParser()
    parser.add_argument('--vps', type=bool, default=False)
    args = parser.parse_args()

    with ThreadPoolExecutor() as executor:
        # Site only start

        if args.vps:
            executor.submit(serve, app=app, host='46.174.48.78', port=5000)  # Fuck warnings
        else:
            executor.submit(serve, app=app, host='localhost', port=5000)  # Fuck warnings

        # Simple site starting:
        #    app.run(
        #        debug=True,
        #        host='localhost',
        #        port=5000
        #    )

        # Site only end
        #

        #
        # Bot Only start
        executor.submit(client.run, token=discord_token)

        # Simple bot starting:
        #    client.run(token=discord_token)

        # Bot Only end
