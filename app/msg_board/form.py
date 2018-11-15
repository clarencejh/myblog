# -*- coding: utf-8 -*-


from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length


class MsgForm(FlaskForm):
    body = TextAreaField('内容', validators=[DataRequired(), Length(1, 400)])
    name = StringField('昵称', validators=[DataRequired(), Length(1, 34)])
