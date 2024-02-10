from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo


class LoginForm(FlaskForm):
    name = StringField('Имя игрока', validators=[DataRequired()])
    # password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired(), EqualTo('confirm_password',
                                                                                     message='Пароли должны совпадать')])
    confirm_password = PasswordField('Подтвердите новый пароль', validators=[DataRequired()])
    submit = SubmitField('Сменить пароль')
