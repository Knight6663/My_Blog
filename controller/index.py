# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年09月27日08时
"""
from json import dumps

from flask import Blueprint, render_template, abort, Response
from math import ceil
from module.article import Article

index = Blueprint("index", __name__)


@index.route('/')
def home():
    article = Article()
    total = ceil(article.get_total_count() / 7)
    result = article.find_limit_with_users(0, 7)
    return render_template('index.html', result=result, page=1, total=total, )


@index.route('/page/<int:page>')
def paginate(page):
    article = Article()
    start = (page - 1) * 7
    total = ceil(article.get_total_count() / 7)
    result = article.find_limit_with_users(start, 7)
    return render_template('index.html', result=result, page=page, total=total)


@index.route('/type/<type_id>/<int:page>')
def classify(type_id, page):
    article = Article()
    start = (page - 1) * 7
    result = article.get_by_type(type_id, start, 7)
    total = ceil(article.get_count_by_type(type_id) / 7)
    return render_template('type.html', result=result, page=page, total=total, type=type_id)


@index.route('/search/<int:page>/<keyword>')
def search(page, keyword):
    keyword = keyword.strip()
    if keyword is None or keyword == '' or '%' in keyword or len(keyword) > 17:
        abort(404)

    article = Article()
    start = (page - 1) * 7
    result = article.search_by_headline(keyword, start, 7)
    total = ceil(article.get_count_by_headline(keyword) / 7)
    return render_template('search.html', result=result, page=page, total=total, keyword=keyword)


@index.route('/side')
def recommend():
    article = Article()
    last, most, recommended = article.find_recent_most_recommended()
    ls = [dict(last), dict(most), dict(recommended)]
    return Response(dumps(ls), mimetype='application/json')
