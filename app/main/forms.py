# -*- coding: utf-8 -*-


# 表单
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,  BooleanField,  PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError, EqualTo

from app.models import User


# 登录表单
class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired(), ])
    remember_me = BooleanField('保持登录')
    submit = SubmitField('登录')


# 注册表单
class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(1, 64)])
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                                    'Usernames must have only letters, numbers, dots or underscores')])

    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', message='两个密码不一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


# 评论表单
class CommitForm(FlaskForm):
    name = StringField('*用户名:', validators=[DataRequired()])
    email = StringField('*邮箱:', validators=[DataRequired(), Email()])
    body = TextAreaField("*评论: ", validators=[DataRequired()])
    submit = SubmitField('提交')


# 文章表单
class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(0, 255)])
    category = SelectField('类别', default=1, coerce=int)
    body = TextAreaField('内容', validators=[DataRequired()])
    link = StringField('链接')