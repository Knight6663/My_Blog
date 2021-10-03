# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年10月02日23时
"""

from flask import Blueprint, render_template, abort

from module.article import Article

article = Blueprint('article', __name__)


@article.route('/article/<int:article_id>')
def read(article_id):
    try:
        article_result = Article().find_by_id(article_id)
        if article_result is None:
            abort(404)
    except:
        abort(500)

    Article().updata_read_count(article_id) # 该文章阅读次数加1
    prev_next = Article().find_prev_and_next_by_id(article_id)

    return render_template('article-user.html', article_result=article_result, prev_next=prev_next)