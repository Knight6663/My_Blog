# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年09月27日08时
"""

from json import dumps
from flask import Blueprint, render_template, abort, Response
from math import ceil
from os import path
from module.article import Article

index = Blueprint("index", __name__)


# @index.route('/')
# def home():
#     # 判断是否存在该页面，如果存在则直接响应，否则正常查询数据库
#     if path.exists('./template/index-static/index-1.html'):
#         return render_template('index-static/index-1.html')
#
#     else:  # 如果不存在该页面，则正常查询数据库，并生成该页面
#         article = Article()
#         result = article.find_limit_with_users(0, 7)
#         total = ceil(article.get_total_count() / 7)
#         content = render_template('index.html', result=result, page=1, total=total)
#
#         # 如果是第一个用户访问，而静态文件不存在，则生成一个
#         with open('./template/index-static/index-1.html', mode='w', encoding='utf-8') as file:
#             file.write(content)
#
#         return content
#
#
# @index.route('/page/<int:page>')
# def paginate(page):
#     if path.exists(f'./template/index-static/index-{page}.html'):  # 判断是否存在该页面，如果存在则直接响应，否则正常查询数据库
#         return render_template(f'index-static/index-{page}.html')
#
#     else:  # 下述代码跟之前版本保持不变，正常查询数据库
#         start = (page - 1) * 7
#         article = Article()
#         result = article.find_limit_with_users(start, 7)
#         total = ceil(article.get_total_count() / 7)
#         content = render_template('index.html', result=result, page=page, total=total)
#
#         # 如果是第一个用户访问，而静态文件不存在，则生成一个
#         with open(f'./template/index-static/index-{page}.html', mode='w', encoding='utf-8') as file:
#             file.write(content)
#
#         return content


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


# ================== 静态化处理 ======================#
@index.route('/static')
def all_static():
    pagesize = 7
    article = Article()
    total = ceil(article.get_total_count() / pagesize)  # 先计算一共有多少页，处理逻辑与分页接口一致
    for page in range(1, total + 1):  # 遍历每一页的内容，从数据库中查询出来，渲染到对应页面中
        start = (page - 1) * pagesize
        result = article.find_limit_with_users(start, pagesize)

        # 将当前页面正常渲染，但不响应给前端，将渲染后的内容写入静态文件
        content = render_template('index.html', result=result, page=page, total=total)

        # 将渲染后的内容写入静态文件,其实content本身就是标准的HTML页面
        with open(f'./template/index-static/index-{page}.html', mode='w', encoding='utf-8') as file:
            file.write(content)

    return '文章列表页面分页静态化处理完成'
