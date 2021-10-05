# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年10月03日23时
"""

from flask import session, request
from sqlalchemy import Table
from common.database import db_connect
from time import strftime

from common.utility import model_list

db_session, md, DBase = db_connect()


class Comment(DBase):
    __table__ = Table('comment', md, autoload=True)

    def insert_comment(self, article_id, content, nickname, ip_address):
        """
        新增一条评论
        :param article_id:文章id
        :param content:评论内容
        :param nickname:评论人的昵称
        :param ip_address:ip地址
        :return:None
        """
        now = strftime('%Y-%m-%d %H:%M:%S')
        comment = Comment(article_id=article_id, content=content, nickname=nickname, ip_address=ip_address,
                          create_time=now)
        try:
            db_session.add(comment)
            db_session.commit()
        except:
            db_session.rollback()

    def insert_reply(self, article_id, comment_id, content, nickname, ip_address):
        """
        对已有的评论进行回复，同样是评论
        :param article_id: 文章id
        :param comment_id: 被回复的评论id
        :param content: 评论(回复)内容
        :param nickname: 昵称
        :param ip_address: ip地址
        :return: None
        """
        now = strftime('%Y-%m-%d %H:%M:%S')
        comment = Comment(article_id=article_id, reply_id=comment_id, content=content, nickname=nickname,
                          ip_address=ip_address, create_time=now)
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

    def find_comment(self, article_id, start, count):
        """
        查询评论，评论可能也需要分页
        :param article_id: 文章id
        :param start: 起始第几条评论
        :param count: 一共多少条评论
        :return: 查询到的评论结果
        """
        result = db_session.query(Comment).filter(Comment.article_id == article_id, Comment.hidden == 0) \
            .order_by(Comment.comment_id.desc()).limit(count).offset(start).all()
        return result

    def find_original_comment(self, article_id, start, count):
        """
        查询原始评论,需要带分页参数
        :param article_id: 文章id
        :param start: 起始第几条评论
        :param count: 一共多少条评论
        :return: 查询到的评论结果
        """
        result = db_session.query(Comment).filter(Comment.article_id == article_id, Comment.hidden == 0,
                                                  Comment.reply_id == 0) \
            .order_by(Comment.comment_id.desc()).limit(count).offset(start).all()
        return result

    def find_reply_comment(self, reply_id):
        """
        查询回复评论,不需要带分页参数
        :param reply_id: 回复id
        :return: 查询到的回复评论结果
        """
        result = db_session.query(Comment).filter(Comment.reply_id == reply_id, Comment.hidden == 0).all()
        return result

    def get_comment_list(self, article_id, start, count):
        """
        根据原始评论和回复评论生成一个关联列表
        :param article_id:文章id
        :param start: 起始第几条评论
        :param count: 一共多少条评论
        :return:原始评论和回复评论的关联列表
        """
        result = self.find_original_comment(article_id, start, count)
        comment_list = model_list(result)  # 原始评论的连接结果
        for comment in comment_list:
            # 查询原始评论对应的回复评论,并转换为列表保存到comment_list中
            result = self.find_reply_comment(comment['comment_id'])
            # 为comment_list列表中的原始评论字典对象添加一个新Key叫reply_list
            # 用于存储当前这条原始评论的所有回复评论,如果无回复评论则列表值为空
            comment['reply_list'] = model_list(result)
        return comment_list  # 将新的数据结构返回给控制器接口

    def update_opinion(self, comment_id, opinion_type):
        """
        更新评论表中的点赞数量
        :param comment_id:评论id
        :param opinion_type: 赞成还是反对
        :return: None
        """
        row = db_session.query(Comment).filter_by(comment_id=comment_id).first()

        if opinion_type == 1:
            row.agree_count += 1
        elif opinion_type == 0:
            row.disagree_count += 1

        try:
            db_session.commit()
        except:
            db_session.rollback()
