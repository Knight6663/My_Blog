# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年10月05日15时
"""


from flask import session, request
from sqlalchemy import Table
from common.database import db_connect
from time import strftime
import random

db_session, md, DBase = db_connect()

class Opinion(DBase):
    __table__ = Table('opinion', md, autoload=True)

    def insert_opinion(self, comment_id, type, ip_address):
        """
        插入评论点赞数据
        :param comment_id: 评论id
        :param type: 赞成还是反对 (1 or 0)
        :param ip_address: ip地址
        :return: None
        """
        now = strftime('%Y-%m-%d %H:%M:%S')

        opinion = Opinion(comment_id=comment_id, type=type, ip_address=ip_address, create_time=now)
        try:
            db_session.add(opinion)
            db_session.commit()
        except:
            db_session.rollback()

    def check_opinion(self, comment_id, ip_address):
        """
        防止单个用户多次赞成或反对，以及防止一个用户即赞成又反对，为此做出判断
        :param comment_id: 评论id
        :param ip_address: ip地址
        :return: 已经点过返回True，反之False
        """
        is_checked = False
        result = db_session.query(Opinion).filter_by(comment_id=comment_id, ip_address=ip_address).all()
        if len(result) > 0:
            is_checked = True

        return is_checked