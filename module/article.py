# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年09月27日08时
"""
from time import strftime

from flask import session
from sqlalchemy import Table, func
from common.database import db_connect
from module.users import Users
from module.sort import Sort

db_session, md, DBase = db_connect()


class Article(DBase):
    __table__ = Table('article', md, autoload=True)

    def find_all(self):
        # 查询所有文章
        result = db_session.query(Article).all()

    def find_article_and_user_by_id(self, article_id):
        # 根据id查询文章
        row = db_session.query(Article, Users.nickname).join(Users, Users.user_id == Article.user_id) \
            .filter(Article.hidden == 0, Article.drafted == 0, Article.article_id == article_id).first()
        return row

    def find_article_by_id(self, article_id):
        row = db_session.query(Article).filter(Article.hidden == 0, Article.drafted == 0,
                                               Article.article_id == article_id).first()
        return row

    def find_article_by_id_and_draft(self, article_id):
        row = db_session.query(Article).filter(Article.hidden == 0, Article.drafted == 1,
                                               Article.article_id == article_id).first()
        return row

    def find_limit_with_users(self, start, count):
        # 指定分页的limit和offset的参数值，同时与用户表做连接查询
        # 三表查询(包含article,users,sort三张表)
        article_result = db_session.query(Article, Users.nickname, Sort.sort_name) \
            .join(Users, Users.user_id == Article.user_id) \
            .join(Sort, Sort.sort_id == Article.sort_id) \
            .filter(Article.hidden == 0, Article.drafted == 0) \
            .order_by(Article.article_id.desc()).limit(count).offset(start).all()
        return article_result

    def get_total_count(self):
        # 返回文章总数量
        count = db_session.query(Article).filter(Article.hidden == 0, Article.drafted == 0).count()
        return count

    def get_by_type(self, type_id, start, count):
        # 根据文章类型获取文章
        result = db_session.query(Article, Users.nickname, Sort.sort_name) \
            .join(Users, Users.user_id == Article.user_id) \
            .join(Sort, Sort.sort_id == Article.sort_id) \
            .filter(Article.hidden == 0, Article.drafted == 0, Article.sort_id == type_id) \
            .order_by(Article.article_id.desc()).limit(count).offset(start).all()
        return result

    def get_count_by_type(self, type_id):
        # 根据文章类型获取总数量
        count = db_session.query(Article).filter(Article.hidden == 0, Article.drafted == 0,
                                                 Article.sort_id == type_id).count()
        return count

    def search_by_headline(self, headline, start, count):
        # 搜索
        result = db_session.query(Article, Users.nickname, Sort.sort_name) \
            .join(Users, Users.user_id == Article.user_id) \
            .join(Sort, Sort.sort_id == Article.sort_id) \
            .filter(Article.hidden == 0, Article.drafted == 0, Article.headline.like('%' + headline + '%')) \
            .order_by(Article.article_id.desc()).limit(count).offset(start).all()
        return result

    def get_count_by_headline(self, headline):
        # 根据搜索内容获取满足条件的总数量
        count = db_session.query(Article).filter(Article.hidden == 0, Article.drafted == 0,
                                                 Article.headline.like('%' + headline + '%')).count()
        return count

    def find_recent_9(self):
        # 最新文章
        result = db_session.query(Article.article_id, Article.headline). \
            filter(Article.hidden == 0, Article.drafted == 0).order_by(Article.create_time.desc()).limit(9).all()
        return result

    def find_read_most_9(self):
        # 阅读量前十
        result = db_session.query(Article.article_id, Article.headline). \
            filter(Article.hidden == 0, Article.drafted == 0).order_by(Article.read_count.desc()).limit(9).all()
        return result

    def find_recommended_9(self):
        # 推荐文章,使用order by rand()随机显示几篇
        result = db_session.query(Article.article_id, Article.headline). \
            filter(Article.hidden == 0, Article.drafted == 0, Article.recommended == 1).order_by(func.rand()).limit(
            9).all()
        return result

    def find_recent_most_recommended(self):
        """
        一次性将三个边栏的数据都传进去
        :return: 一次性将边栏三个全部传进去
        """
        recent = self.find_recent_9()
        most = self.find_read_most_9()
        recommended = self.find_recommended_9()
        return recent, most, recommended

    def updata_read_count(self, article_id):
        """
        每阅读一次文章，将该文章的阅读次数加1
        :param article_id: 文章id
        :return:None
        """
        article = db_session.query(Article).filter_by(article_id=article_id).first()
        article.read_count += 1
        try:
            db_session.commit()
        except:
            db_session.rollback()

    def find_headline_by_id(self, article_id):
        """
        根据文章id查询文章标题
        :param article_id:文章id
        :return: 文章标题
        """
        res = db_session.query(Article.headline).filter_by(article_id=article_id).first()
        return res.headline

    def find_prev_and_next_by_id(self, article_id):
        """
        根据文章id查找符合条件的上一篇文章和下一篇文章
        :param article_id: 文章id
        :return: 字典类型，上一篇文章和下一篇文章信息
        """
        d = {}

        # 查询比当前编号小的当中最大的一个
        res = db_session.query(Article).filter(Article.hidden == 0, Article.drafted == 0,
                                               Article.article_id < article_id).order_by(
            Article.article_id.desc()).limit(1).first()

        # 如果当前已经是第一篇，那么上一篇就是这一篇
        if res is None:
            prev_id = article_id
        else:
            prev_id = res.article_id

        d['prev_id'] = prev_id
        d['prev_headline'] = self.find_headline_by_id(prev_id)

        # 查询比当前编号大的当中最小的一个
        res = db_session.query(Article).filter(Article.hidden == 0, Article.drafted == 0,
                                               Article.article_id > article_id).order_by(
            Article.article_id).limit(1).first()

        # 如果当前已经是最后一篇，那么下一篇就是这一篇
        if res is None:
            next_id = article_id
        else:
            next_id = res.article_id

        d['next_id'] = next_id
        d['next_headline'] = self.find_headline_by_id(next_id)

        return d

    def update_reply_count(self, article_id):
        """
        当发表或回复评论之后，为文章表字段reply_count加1
        :param article_id: 文章id
        :return: None
        """
        row = db_session.query(Article).filter_by(article_id=article_id).first()
        row.reply_count += 1
        try:
            db_session.commit()
        except:
            db_session.rollback()

    def insert_article(self, sort_id, headline, content, thumbnail, drafted=0):
        """
        插入一篇新的文章，是否为草稿通过参数进行区分
        :param sort_id: 分类id
        :param headline: 标题
        :param content: 内容
        :param thumbnail: 文章缩略图
        :param drafted: 是否为草稿，默认为0
        :return: 这篇文章的id
        """
        now = strftime('%Y-%m-%d %H:%M:%S')
        user_id = session.get('user_id')
        # 其他字段在数据库中均已设置好默认值，无须手工插入
        article = Article(user_id=user_id, sort_id=sort_id, headline=headline, content=content,
                          thumbnail=thumbnail, drafted=drafted,
                          create_time=now, update_time=now)
        try:
            db_session.add(article)
            db_session.commit()
        except:
            db_session.rollback()

        return article.article_id  # 将新的文章编号返回，便于前端页面跳转

    def update_article(self, article_id, sort_id, headline, content, thumbnail, drafted=0):
        """
        根据文章编号更新文章的内容，可用于文章编辑或草稿修改，以及基于草稿的发布
        :param article_id: 文章id
        :param sort_id: 分类id
        :param headline: 标题
        :param content: 内容
        :param thumbnail: 缩略图
        :param drafted: 是否为草稿
        :return: 该文章id
        """
        now = strftime('%Y-%m-%d %H:%M:%S')
        row = db_session.query(Article).filter_by(article_id=article_id).first()
        row.sort_id = sort_id
        row.headline = headline
        row.content = content
        row.thumbnail = thumbnail
        row.drafted = drafted

        row.update_time = now  # 修改文章的更新时间
        try:
            db_session.commit()
        except:
            db_session.rollback()
        return article_id  # 继续将文章ID返回调用处

    # =========== 以下方法用于后台管理类操作 ================== #

    def find_all_except_draft(self, start, count):
        """
        查询article表中除草稿外的所有数据并返回结果集
        :param start:
        :param count:
        :return: article表中除草稿外的所有数据
        """
        result = db_session.query(Article).filter(Article.drafted == 0).order_by(
            Article.article_id.desc()).limit(count).offset(start).all()
        return result

    def get_count_except_draft(self):
        """
        查询除草稿外的所有文章的总数量
        :return: 除草稿外的所有文章的总数量
        """
        count = db_session.query(Article).filter(Article.drafted == 0).count()
        return count

    def find_by_type_except_draft(self, start, count, sort_id):
        """
        按照文章分类进行查询
        :param start:
        :param count:
        :param sort_id: 分类id
        :return: 分页结果集和不分页的总数量
        """
        if sort_id == 0:
            result = self.find_all_except_draft(start, count)
            total = self.get_count_except_draft()
        else:
            result = db_session.query(Article).filter(Article.drafted == 0,
                                                      Article.sort_id == sort_id).order_by(Article.article_id.desc()) \
                .limit(count).offset(start).all()
            total = db_session.query(Article).filter(Article.drafted == 0,
                                                     Article.sort_id == sort_id).count()
        return result, total

    def find_by_headline_except_draft(self, headline):
        """
        按照标题模糊查询（不含草稿）
        :param headline: 标题
        :return: 查询结果
        """
        result = db_session.query(Article).filter(Article.drafted == 0,
                                                  Article.headline.like('%' + headline + '%')) \
            .order_by(Article.article_id.desc()).all()
        return result

    def switch_hidden(self, article_id):
        """
        切换文章的隐藏状态：1表示隐藏，0表示显示
        :param article_id: 文章id
        :return: 当前最新状态
        """
        row = db_session.query(Article).filter_by(article_id=article_id).first()
        if row.hidden == 1:
            row.hidden = 0
        else:
            row.hidden = 1
        try:
            db_session.commit()
        except:
            db_session.rollback()
        return row.hidden  # 将当前最新状态返回给控制层

    def switch_recommended(self, article_id):
        """
        切换文章的推荐状态：1表示推荐，0表示正常
        :param article_id: 文章id
        :return: 当前最新状态
        """
        row = db_session.query(Article).filter_by(article_id=article_id).first()
        if row.recommended == 1:
            row.recommended = 0
        else:
            row.recommended = 1
        try:
            db_session.commit()
        except:
            db_session.rollback()
        return row.recommended

    def find_all_by_draft(self, start, count):
        """
        查询article表中除草稿外的所有数据并返回结果集
        :param start:
        :param count:
        :return: article表中除草稿外的所有数据
        """
        result = db_session.query(Article).filter(Article.drafted == 1).order_by(
            Article.article_id.desc()).limit(count).offset(start).all()
        return result

    def get_count_by_draft(self):
        """
        查询是草稿的所有文章的总数量
        :return: 除草稿外的所有文章的总数量
        """
        count = db_session.query(Article).filter(Article.drafted == 1).count()
        return count

    def find_by_type_by_draft(self, start, count, sort_id):
        """
        按照文章分类进行查询
        :param start:
        :param count:
        :param sort_id: 分类id
        :return: 分页结果集和不分页的总数量
        """
        if sort_id == 0:
            result = self.find_all_by_draft(start, count)
            total = self.get_count_by_draft()
        else:
            result = db_session.query(Article).filter(Article.drafted == 1,
                                                      Article.sort_id == sort_id).order_by(Article.article_id.desc()) \
                .limit(count).offset(start).all()
            total = db_session.query(Article).filter(Article.drafted == 1,
                                                     Article.sort_id == sort_id).count()
        return result, total

    def find_by_headline_by_draft(self, headline):
        """
        按照标题模糊查询（只含草稿）
        :param headline: 标题
        :return: 查询结果
        """
        result = db_session.query(Article).filter(Article.drafted == 1,
                                                  Article.headline.like('%' + headline + '%')) \
            .order_by(Article.article_id.desc()).all()
        return result
