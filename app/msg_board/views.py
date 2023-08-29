# -*- coding: utf-8 -*-

from flask import render_template, flash, url_for, redirect, request, current_app
from app.msg_board import msg
from app.msg_board.form import MsgForm
from app.libs import db
from app.models import Message


@msg.route('/msg', methods=['GET', 'POST'])
def index():
    form = MsgForm()
    page = request.args.get('page', 1, type=int)
    validate = form.validate()
    if validate:
        with db.auto_commit():
            msg = Message()
            msg.name = form.name.data
            msg.body = form.body.data
            db.session.add(msg)
        flash('发表成功')
        return redirect(url_for('msg.index'))
    if request.method == "POST" and not validate:
        flash('字符太长')

    pagination = Message.query.order_by(Message.timestamp.desc()).paginate(
        page, per_page=current_app.config['MESSAGES_SHOW_PER_PAGE'], error_out=False)
    msgs = pagination.items
    return render_template('message_board.html', form=form, msgs=msgs, pagination=pagination)


