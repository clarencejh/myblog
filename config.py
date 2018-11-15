# -*- coding: utf-8 -*-

# 生产环境不要设置为 True
DEBUG = True

SECRET_KEY = b'welcome to blog-flask by "clarence" {{{{{{{{{{{{{'
SQLALCHEMY_TRACK_MODIFICATIONS = False
# 首页显示的文章数量
BLOG_POSTS_PER_PAGE = 8
# 留言板每页显示的条数
MESSAGES_SHOW_PER_PAGE = 20

# 数据库相关
DIALECT = 'mysql'
DRIVER = 'cymysql'
USENAME = ''
PASSWORD = ''
dbHOST = '127.0.0.1'
PORT = 3306
DATABASE = ''

SQLALCHEMY_DATABASE_URI = '{DIALECT}+{DRIVER}://{USENAME}:{PASSWORD}@{dbHOST}:{PORT}/{DATABASE}?charset=utf8'.format(
    DIALECT=DIALECT, DRIVER=DRIVER, USENAME=USENAME, PASSWORD=PASSWORD, dbHOST=dbHOST, PORT=PORT, DATABASE=DATABASE)
