# -*- coding: utf-8 -*-
import hashlib
from datetime import datetime

import bleach
from flask import current_app, flash, request
from markdown import markdown

from app.libs import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES, True),
            'Moderator': (
                Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_ARTICLES | Permission.MODERATE_COMMENTS,
                False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role "%r" > ' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    # 自我介绍
    about_me = db.Column(db.Text(), default='请设置个人介绍')
    # 注册时间
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    # 最后访问日期
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    # 关联用户权限
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    # 关联用户文章
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # 用户是否验证邮箱
    confirmed = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    @staticmethod
    def reset_password(token, newpassword):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        with db.auto_commit():
            user.password = newpassword
            db.session.add(user)
        return True

    def generate_change_email_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            flash('验证错误, 请重试')
            return False
        new_email = data.get('new_email')
        if new_email is None:
            flash('验证错误, 请重试')
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            flash('该邮箱已经注册')
            return False
        with db.auto_commit():
            self.email = new_email
            db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    @property
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def gravatar(self, size=100, default='mp', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default,
                                                                     rating=rating)

    # 更新用户最后登录时间
    def ping(self):
        with db.auto_commit():
            self.last_seen = datetime.utcnow()
            db.session.add(self)

    def __repr__(self):
        return '<User "%r ">' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class Permission:
    '''
        关注用户                  0b00000001（0x01） 关注其他用户
        在他人的文章中发表评论      0b00000010（0x02） 在他人撰写的文章中发布评论
        写文章                   0b00000100（0x04） 写原创文章
        管理他人发表的评论         0b00001000（0x08） 查处他人发表的不当评论
        管理员权限                0b10000000（0x80） 管理网站
    '''
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), index=True, nullable=False)
    body = db.Column(db.Text(), nullable=False)
    link = db.Column(db.Text())

    timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    reads = db.Column(db.Integer, index=True, default=0)
    zans = db.Column(db.Integer, index=True, default=0)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    commits = db.relationship('Commit', backref='post', lazy='dynamic')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    def add_reads(self):
        with db.auto_commit():
            self.reads += 1
            db.session.add(self)

    def add_zans(self):
        with db.auto_commit():
            if self.zans < 9999:
                self.zans += 1
                if self.reads >= 1:
                    self.reads -= 1
                db.session.add(self)
                return True
            else:
                return False

    def __repr__(self):
        return "<Post %s>" % self.title


class Commit(db.Model):
    __tablename__ = 'commits'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64), index=True)
    body = db.Column(db.Text())
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def gravatar(self, size=100, default='mp', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default,
                                                                     rating=rating)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(32), index=True, nullable=False)
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    @staticmethod
    def insert_category(name):
        pass

    def __repr__(self):
        return '<Categort %s>'%self.category_name


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    body = db.Column(db.Text())
    timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
