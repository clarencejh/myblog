
# blog-flask



首先应设置 数据库相关 

---
#### 切换到主目录:
```
python manage.py db init
python manage.py db migrate
python manage.py db upgraed
```
创建表即可


#### 然后执行 

    python manage.py init
创建管理员账号密码:
    
依次要输入的为: 

    email  ->  登录账号

    username -> 用户名

    password -> 密码 


#### 目前没有在主页显示登录, 管理员入口

需要手动输入, 管理员界面为 /admin


#### 另外, 在创建完管理员之后, 可自行去后台设置分类

程序已经自行创建一个 "default" 分类


### 目前完善开发中.....
    网站功能虽然简单, 但麻雀虽小五脏俱全


最后: 网站前端, 直接套用的 这个网站.... https://www.golaravel.com/

#### git_test