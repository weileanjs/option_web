#coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField,BooleanField,PasswordField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('用户名',validators=[DataRequired()])
    password = PasswordField('密码',validators=[DataRequired()])
    remember_me = BooleanField('remember me',default=False)
