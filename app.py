from flask import Flask, render_template, url_for, redirect, flash
from flask_login import UserMixin, logout_user, login_required, login_user, current_user, LoginManager
from flask_wtf.csrf import CSRFProtect
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship

# TODO: from werkzeug.security import check_password_hash

from forms.login import LoginForm

csrf = CSRFProtect()
password = 'SbDwFqC@+iD5erM7QAYHE@Jo'
encoded_password = quote_plus(password)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'LinyX_secret_key'
app.config['FLASK_DEBUG'] = 1
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'mysql+mysqlconnector://u11944_HjaF3FL0R2:{encoded_password}@d4.aurorix.net:3306/s11944_anarchy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
logmanager = LoginManager()
logmanager.init_app(app)


class Donation(db.Model):
    __tablename__ = 'donations'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False)
    player_name = Column(String, ForeignKey('players.name'), nullable=False)
    price = Column(Float, nullable=False)
    duration = Column(Integer, default=0)

    player = relationship('Player', back_populates='donations')
    purchases = relationship('Purchase', back_populates='donations')


class Player(UserMixin, db.Model):
    __tablename__ = 'players'
    id = Column(Integer, autoincrement=True, primary_key=True)
    uuid = Column(String(36), nullable=False, unique=True)
    name = Column(String, nullable=False, unique=True)
    ip = Column(String(255))

    donations = relationship('Donation', back_populates='player')
    password = relationship('Password', back_populates='player')
    purchases = relationship('Purchase', back_populates='player')


class Password(db.Model):
    __tablename__ = 'passwords'
    id = Column(Integer, primary_key=True)
    player_name = Column(String, ForeignKey('players.name'), unique=True, nullable=False)
    password = Column(String, nullable=False)

    player = relationship('Player', back_populates='password')


class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = Column(Integer, autoincrement=True, primary_key=True)
    player_name = Column(String, ForeignKey('players.name'), nullable=False)
    donation_name = Column(String, ForeignKey('donations.name'), nullable=False)
    purchase_date = Column(DateTime(timezone=True), server_default=func.now())

    player = relationship('Player', back_populates='purchases')
    donations = relationship('Donation', back_populates='purchases')


@app.route('/')
def index():
    donations = Donation.query.all()
    return render_template('index.html', donations=donations)


@app.route('/donation/<int:id>')
def donation_detail(id):
    donation = Donation.query.get(id)
    return render_template('donation_detail.html', donation=donation)


@app.route('/purchase/<int:id>')
@login_required
def purchase(id):
    donation = Donation.query.get(id)
    if donation:
        new_purchase = Purchase(player_name=current_user.name, donation_name=donation.name)
        db.session.add(new_purchase)
        db.session.commit()
        flash('Покупка успешно совершена!', 'success')
    return redirect(url_for('index'))


@app.route('/account')
@login_required
def account():
    purchases = Purchase.query.filter_by(player_name=current_user.name).all()
    return render_template('account.html', purchases=purchases)


@logmanager.user_loader
def load_user(user_id):
    return Player.query.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Предполагается, что у вас есть форма LoginForm для входа

    if form.validate_on_submit():
        player_name = form.name.data
        entered_password = form.password.data
        player = Player.query.filter_by(name=player_name).first()

        if player:
            password_entry = Password.query.filter_by(player_name=player_name).first().password
            if password_entry == entered_password:
                login_user(player, remember=form.remember_me.data)
                return redirect(url_for('index'))

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из аккаунта.', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

# TODO: проверить работоспособность самой главной таблицы на возможность покупки и тд.
#  проверить, как работает сама покупка
