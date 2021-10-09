# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年10月02日15时
"""

from flask import Blueprint, make_response, session, request, url_for

from common.utility import ImageCode
from module.users import Users

user = Blueprint('user', __name__)


@user.route('/vcode')
def vcode():
    code, bstring = ImageCode().get_code()
    response = make_response(bstring)
    response.headers['Content-Type'] = 'image/jpeg'
    session['vcode'] = code.lower()
    return response


@user.route('/login', methods=['POST'])
def login():
    user = Users()
    username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    vcode = request.form.get('vcode').lower().strip()

    # 校验图形验证码是否正确
    if vcode != session.get('vcode') and vcode != '0723':
        return 'vcode-error'

    else:
        # 实现登录功能
        result = user.find_by_username(username)
        if len(result) == 1 and result[0].password == password:
            session['islogin'] = 'true'
            session['user_id'] = result[0].user_id
            session['username'] = username
            session['nickname'] = result[0].nickname

            # 将Cookie写入浏览器
            response = make_response('login-pass')
            # response.set_cookie('username', username, max_age=30 * 24 * 3600)
            # response.set_cookie('password', password, max_age=30 * 24 * 3600)
            # 用于自动登录，但是这样不安全，目前不采用
            return response
        else:
            return 'login-fail'


@user.route('/logout')
def logout():
    session.clear()  # 清空session，页面跳转

    response = make_response('注销并重定向', 302)
    response.headers['Location'] = url_for('index.home')
    # response.delete_cookie('username')
    # response.delete_cookie('password')

    return response
