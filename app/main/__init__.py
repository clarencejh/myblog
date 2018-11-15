# -*- coding: utf-8 -*-

from flask import Blueprint

from app.models import Permission, Category, Post
from app.libs import db

main = Blueprint('main', __name__)

from . import views


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.app_context_processor
def inject_recent_article():
    recent_articles = Post.query.order_by(Post.timestamp.desc()).limit(3).all()
    return dict(recent_articles=recent_articles)


@main.app_context_processor
def inject_category():
    categories = Category.query.filter_by().all()
    return dict(categories=categories)