# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年09月27日07时
"""
from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
import pymysql

pymysql.install_as_MySQLdb()  # 解决错误  ModuleNotFoundError: No module named 'MySQLdb'

app = Flask(__name__, template_folder='template', static_url_path='/', static_folder='resource')
app.config['SECRET_KEY'] = os.urandom(24)  # 解决session的随机种子

# 使用集成方式处理SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:2211@localhost:3306/lrc's-blog?charset=utf8"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # True:跟踪数据库的修改，及时发送信号
app.config['WHOOSH_BASE'] = 'whoosh_index'
app.config['WHOOSH_ENABLE'] = True

# 实例化db对象
db = SQLAlchemy(app)


# 定义404错误页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error-404.html')


# 定义500错误页面
@app.errorhandler(500)
def server_error(e):
    return render_template('error-500.html')


def custom_truncate(s, length, end=''):
    """
    重构truncate过滤器
    :param s: 字符串
    :param length: 限定长度
    :param end: 结尾字符，超出限定长度就将多余字符替换为...
    :return: 经过过滤器处理过的字符串
    """
    count = 0
    new = ''
    for c in s:
        new += c
        if ord(c) <= 128:
            count += 0.5
        else:
            count += 1
            if count > length:
                end = '...'
                break
    return new + end


# 注册重构的truncate过滤器
app.jinja_env.filters.update(truncate=custom_truncate)


# 定义一个函数来处理类型的传递，供模板页面使用，可以替换三表连接
@app.context_processor
def gettype():
    article_type = {
        '1': 'Python',
        '2': 'Java',
        '3': 'Web前端',
        '4': '数据科学',
        '5': '计算机基础',
        '6': '机器学习',
        '7': '其他',
    }
    return dict(article_type=article_type)


@app.route('/admin/login')
def test():
    return render_template('login.html')


@app.context_processor
def get_side():
    article = Article()
    recent, most, recommended = article.find_recent_most_recommended()
    return dict(recent=recent, most=most, recommended=recommended)


if __name__ == '__main__':
    from controller.index import *

    app.register_blueprint(index)

    from controller.user import *

    app.register_blueprint(user)

    from controller.article import *

    app.register_blueprint(article)

    from controller.comment import *

    app.register_blueprint(comment)

    from controller.ueditor import *

    app.register_blueprint(ueditor)

    from controller.admin import *

    app.register_blueprint(admin)

    app.run(debug=True, port=80)
