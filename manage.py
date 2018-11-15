# -*- coding: utf-8 -*-

import os
from app import create_app
from app.libs import db
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate

from app.models import Role, User, Category

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)


# @manager.command
# def test():
#     """ Run the unit tests"""
#     import unittest
#     tests = unittest.TestLoader().discover('tests')
#     unittest.TextTestRunner(verbosity=2).run(tests)
@manager.command
def init():
    print('正在创建 权限管理 类别.....')
    _role = Role()
    _role.insert_roles()
    print('成功创建权限管理! \n')
    print('-'*30)

    print('正在创建默认分类...')
    category = Category()
    print('创建成功! 分类: default,  \n')
    print('-'*30)

    print('请先设置管理员账号')
    email = input('请设置邮箱, 作为登录账号(email): ')
    username = input('请输入用户名(username): ')
    password = input('请输入密码(password)  "  请 注 意!   明文显示": ')
    user = User()
    role = Role.query.get(3)
    with db.auto_commit():
        category.category_name = 'default'
        user.email = email
        user.username = username
        user.password = password
        user.role = role
        db.session.add(user)
        db.session.add(category)

    print('创建管理员成功')
    print('请前往 /admin/ 下的 "类别管理" 创建 "类别" ')


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command('db', MigrateCommand)
manager.add_command('shell',  Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
