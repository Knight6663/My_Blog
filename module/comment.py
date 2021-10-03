# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年10月03日23时
"""

from flask import session, request
from sqlalchemy import Table
from common.database import db_connect
from time import strftime

db_session, md, DBase = db_connect()


class Comment(DBase):
    __table__ = Table('comment', md, autoload=True)

    def insert_comment(self, article_id, content, ip_address):
        """
        新增一条评论
        :param article_id:文章id
        :param content:评论内容
        :param ip_address:ip地址
        :return:None
        """
        now = strftime('%Y-%m-%d %H:%M:%S')
        comment = Comment(article_id=article_id, content=content, ip_address=ip_address, create_time=now)
        try:
            db_session.add(comment)
            db_session.commit()
        except:
            db_session.rollback()

    def find_by_articleid(self, article_id):
        """
        根据文章编号查询所有评论
        :param article_id:文章id
        :return:所有评论结果
        """
        result = db_session.query(Comment).filter_by(article_id=article_id, hidden=0, reply_id=0).all()
        return result

    def check_limit_per_5(self):
        """
        根据用户编号和日期进行查询是否已经超过每天5条限制
        :return:True of False
        """
        start = strftime("%Y-%m-%d 00:00:00")  # 当天的起始时间
        end = strftime("%Y-%m-%d 23:59:59")  # 当天的结束时间
        result = db_session.query(Comment).filter(Comment.create_time.between(start, end)).all()
        if len(result) >= 5:
            return True  # 返回True表示今天已经不能再发表评论
        else:
            return False
