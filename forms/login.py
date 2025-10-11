from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    name = StringField('Имя игрока', validators=[DataRequired()])
    submit = SubmitField('Войти')
