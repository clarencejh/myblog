# -*- coding: utf-8 -*-

from datetime import datetime
from flask import render_template, url_for, redirect, flash, abort, request, current_app, session
from flask_login import login_user, current_user, login_required, logout_user
from app.models import User, Post, Commit, Category
from app.libs import db
from app.decorators import admin_required, permission_required
from app.main import main
from app.main.forms import LoginForm, PostForm, CommitForm, RegistrationForm, SearchForm
from sqlalchemy import and_, or_


@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'], error_out=False
    )
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination, current_time=datetime.utcnow())


# 表单验证, 然后重定向搜索
@main.route('/search-red/', methods=['POST'])
def search_red():
    form = SearchForm()
    if form.validate_on_submit():
        kw = form.content.data
        return redirect(url_for('main.search', kw=kw))
    return redirect(url_for('main.index'))


@main.route('/search/')
def search():
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('kw', 'python')
    pagination = Post.query.filter(
        or_(Post.title.like("%" + keyword + "%"),
            Post.body.like("%" + keyword + "%"),
            )).paginate(
        page, per_page=10, error_out=False)
    posts = pagination.items
    return render_template('search.html', pagination=pagination, posts=posts)

    #
    # pagination = Post.query.filter(
    #     or_(Post.title.like("%" + form.content.data + "%")
    #         )).paginate(
    #     page, per_page=10, error_out=False)
    # posts = pagination.items
    # return render_template('search.html', searchform=form, pagination=pagination, posts=posts)


def get_category():
    categories = Category.query.filter().all()
    return [(category.id, category.category_name) for category in categories]


@main.route('/post-article/', methods=['GET', 'POST'])
@login_required
@admin_required
def post_article():
    choices = get_category()
    form = PostForm()
    form.category.choices = choices
    if form.validate_on_submit() and current_user.is_authenticated:
        with db.auto_commit():
            post = Post()
            post.title = form.title.data
            post.body = form.body.data
            post.link = form.link.data
            _category = Category.query.get_or_404(form.category.data)
            post.category = _category
            post.author = current_user._get_current_object()
            db.session.add(post)
        flash('你发表了一篇文章.')
        return redirect(url_for('main.index'))
    return render_template('post_article.html', form=form)


@main.route('/edit-article/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_article(id):
    choices = get_category()
    form = PostForm()
    form.category.choices = choices
    post = Post.query.get_or_404(id)
    if form.validate_on_submit() and current_user.is_authenticated:
        with db.auto_commit():
            post.title = form.title.data
            post.body = form.body.data
            post.link = form.link.data
            _category = Category.query.get_or_404(form.category.data)
            post.category = _category
            db.session.add(post)
        flash('你修改了一篇文章.')
        return redirect(url_for('main.index'))
    form.title.data = post.title
    form.body.data = post.body
    form.link.data = post.link
    form.category.data = post.category_id
    return render_template('edit_article.html', form=form, post=post)


@main.route('/article/<int:id>', methods=['GET', 'POST'])
def article(id):
    form = CommitForm()
    post = Post.query.get_or_404(id)
    if request.method == 'GET':
        # 阅读数增加限制
        if not session.get('article_id_reads'):
            session['article_id_reads'] = []
        if id not in session.get('article_id_reads'):
            post.add_reads()
            session.get('article_id_reads').append(id)
        commits = post.commits.order_by().limit(current_app.config['COMMIT_SHOW_LIMIT']).all()
        return render_template('article.html', post=post, commits=commits, form=form)

    if request.method == 'POST':
        if form.validate_on_submit():
            with db.auto_commit():
                commit = Commit()
                commit.name = form.name.data
                commit.email = form.email.data
                commit.body = form.body.data
                commit.post = post
                db.session.add(commit)
            flash('评论成功')
            return redirect(url_for('main.article', id=id))
        return redirect(url_for('main.article', id=id))


@main.route('/article_zan/<int:id>')
def article_zans(id):
    post = Post.query.get_or_404(id)
    # 点赞限制
    if not session.get('article_id_zans'):
        session['article_id_zans'] = []
    if id not in session.get('article_id_zans'):
        post.add_zans()
        session.get('article_id_zans').append(id)
        flash('感谢你的点赞')
    else:
        flash('你已经点过赞了')

    return redirect(url_for('main.article', id=id))


# 用户登录路由
@main.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))

        flash('用户名或密码错误')
    return render_template('login.html', form=form)


# 用户注册路由
@main.route('/register/', methods=['GET', 'POST'])
@admin_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        with db.auto_commit():
            user = User()
            user.email = form.email.data
            user.username = form.username.data
            user.password = form.password.data
            db.session.add(user)

        # token = user.generate_confirmation_token()
        # send_email(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
        # flash('已经发送一个确认邮件至您的邮箱, 请查收.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


# 用户登出路由
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("您已退出登录")
    return redirect(url_for('main.index'))


@main.route('/category/')
def category_page():
    page = request.args.get('page', 1, type=int)
    category_name = request.args.get('category_name')
    category = Category.query.filter_by(category_name=category_name).first()
    pagination = category.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=10, error_out=False
    )
    posts = pagination.items
    return render_template('categort.html', posts=posts, category_name=category_name, pagination=pagination)
