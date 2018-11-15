# -*- coding: utf-8 -*-
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView as _AdminIndexView
from flask_admin import expose
from flask_login import login_required
from app.decorators import admin_required
from app.models import User, Post, Commit, Message
from app.libs import db


def add_admin(admin):
    from app.models import User, Post, Commit, Message, Category
    admin.add_view(UserViewAdmin(User, db.session, name='用户管理'))
    admin.add_view(ArticleViewAdmin(Post, db.session, name='文章管理'))
    admin.add_view(MessageViewAdmin(Category, db.session, name='类别管理'))
    admin.add_view(CommitViewAdmin(Commit, db.session, name='评论管理'
                                   ))
    admin.add_view(MessageViewAdmin(Message, db.session, name='留言板管理'))


class AdminIndexView(_AdminIndexView):
    @expose('/')
    @login_required
    @admin_required
    def index(self):
        return self.render('admin.html')


class UserViewAdmin(ModelView):
    # 这三个变量定义管理员是否可以增删改，默认为True
    # can_delete = False
    # can_edit = False
    # can_create = False
    # 这里是为了自定义显示的column名字


    # 如果不想显示某些字段，可以重载这个变量
    column_exclude_list = (
        'password_hash',
    )
    column_searchable_list = (User.username,)


class ArticleViewAdmin(ModelView):
    column_searchable_list = (Post.title, Post.body)


class CommitViewAdmin(ModelView):
    column_searchable_list = (Commit.body, )


class MessageViewAdmin(ModelView):
    column_searchable_list = (Message.body, Message.name)
