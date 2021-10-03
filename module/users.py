# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年09月27日08时
"""
from sqlalchemy import Table
from common.database import db_connect

db_session, md, DBase = db_connect()


class Users(DBase):
    __table__ = Table('users', md, autoload=True)

    def find_by_username(self, username):
        """
        查询用户名，用于登录校验
        :param username: 用户名
        :return:
        """
        result = db_session.query(Users).filter_by(username=username).all()
        return result

    def find_by_userid(self, userid):
        user = db_session.query(Users).filter_by(userid=userid).one()
        return user