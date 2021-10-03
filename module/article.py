# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年09月27日08时
"""
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

    def find_by_id(self, artcile_id):
        # 根据id查询文章
        row = db_session.query(Article, Users.nickname).join(Users, Users.user_id == Article.user_id) \
            .filter(Article.hidden == 0, Article.article_id == artcile_id).first()
        return row

    def find_limit_with_users(self, start, count):
        # 指定分页的limit和offset的参数值，同时与用户表做连接查询
        # 三表查询(包含article,users,sort三张表)
        article_result = db_session.query(Article, Users.nickname, Sort.sort_name) \
            .join(Users, Users.user_id == Article.user_id) \
            .join(Sort, Sort.sort_id == Article.sort_id) \
            .filter(Article.hidden == 0) \
            .order_by(Article.article_id.desc()).limit(count).offset(start).all()
        return article_result

    def get_total_count(self):
        # 返回文章总数量
        count = db_session.query(Article).filter(Article.hidden == 0).count()
        return count

    def get_by_type(self, type_id, start, count):
        # 根据文章类型获取文章
        result = db_session.query(Article, Users.nickname, Sort.sort_name) \
            .join(Users, Users.user_id == Article.user_id) \
            .join(Sort, Sort.sort_id == Article.sort_id) \
            .filter(Article.hidden == 0, Article.sort_id == type_id) \
            .order_by(Article.article_id.desc()).limit(count).offset(start).all()
        return result

    def get_count_by_type(self, type_id):
        # 根据文章类型获取总数量
        count = db_session.query(Article).filter(Article.hidden == 0, Article.sort_id == type_id).count()
        return count

    def search_by_headline(self, headline, start, count):
        # 搜索
        result = db_session.query(Article, Users.nickname, Sort.sort_name) \
            .join(Users, Users.user_id == Article.user_id) \
            .join(Sort, Sort.sort_id == Article.sort_id) \
            .filter(Article.hidden == 0, Article.headline.like('%' + headline + '%')) \
            .order_by(Article.article_id.desc()).limit(count).offset(start).all()
        return result

    def get_count_by_headline(self, headline):
        # 根据搜索内容获取满足条件的总数量
        count = db_session.query(Article).filter(Article.hidden == 0,
                                                 Article.headline.like('%' + headline + '%')).count()
        return count

    def find_recent_9(self):
        # 最新文章
        result = db_session.query(Article.article_id, Article.headline). \
            filter(Article.hidden == 0).order_by(Article.article_id.desc()).limit(9).all()
        return result

    def find_read_most_9(self):
        # 阅读量前十
        result = db_session.query(Article.article_id, Article.headline). \
            filter(Article.hidden == 0).order_by(Article.read_count.desc()).limit(9).all()
        return result

    def find_recommended_9(self):
        # 推荐文章,使用order by rand()随机显示几篇
        result = db_session.query(Article.article_id, Article.headline). \
            filter(Article.hidden == 0, Article.recommended == 1).order_by(func.rand()).limit(9).all()
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
        db_session.commit()

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
        res = db_session.query(Article).filter(Article.hidden == 0, Article.article_id < article_id).order_by(
            Article.article_id.desc()).limit(1).first()

        # 如果当前已经是第一篇，那么上一篇就是这一篇
        if res is None:
            prev_id = article_id
        else:
            prev_id = res.article_id

        d['prev_id'] = prev_id
        d['prev_headline'] = self.find_headline_by_id(prev_id)

        # 查询比当前编号大的当中最小的一个
        res = db_session.query(Article).filter(Article.hidden == 0, Article.article_id > article_id).order_by(
            Article.article_id).limit(1).first()

        # 如果当前已经是最后一篇，那么下一篇就是这一篇
        if res is None:
            next_id = article_id
        else:
            next_id = res.article_id

        d['next_id'] = next_id
        d['next_headline'] = self.find_headline_by_id(next_id)

        return d
