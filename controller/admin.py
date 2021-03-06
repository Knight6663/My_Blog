# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年10月06日11时
"""

from flask import Blueprint, render_template, session, request, redirect
from module.article import Article
from math import ceil

admin = Blueprint("admin", __name__)


@admin.before_request
def before_admin():
    if request.path == '/admin/login':
        return None

    if session.get('islogin') != 'true':
        return redirect('/admin/login')


# 为系统管理首页填充文章列表，并绘制分页栏
@admin.route('/admin')
def sys_admin():
    pagesize = 50
    article = Article()
    result = article.find_all_except_draft(0, pagesize)
    total = ceil(article.get_count_except_draft() / pagesize)
    return render_template('admin.html', page=1, result=result, total=total)


@admin.route('/admin/prepost')
def pre_post():
    return render_template('post.html')


# 为系统管理首页的文章列表进行分页查询
@admin.route('/admin/article/<int:page>')
def admin_article(page):
    pagesize = 50
    start = (page - 1) * pagesize
    article = Article()
    result = article.find_all_except_draft(start, pagesize)
    total = ceil(article.get_count_except_draft() / pagesize)
    return render_template('admin.html', page=page, result=result, total=total)


@admin.route('/admin/draft')
def admin_draft():
    pagesize = 50
    article = Article()
    result = article.find_all_by_draft(0, pagesize)
    total = ceil(article.get_count_by_draft() / pagesize)
    return render_template('admin-draft.html', page=1, result=result, total=total)


@admin.route('/admin/draft/<int:page>')
def draft_page(page):
    pagesize = 50
    start = (page - 1) * pagesize
    article = Article()
    result = article.find_all_by_draft(start, pagesize)
    total = ceil(article.get_count_by_draft() / pagesize)
    return render_template('admin-draft.html', page=page, result=result, total=total)


@admin.route('/admin/edit/<int:article_id>')
def admin_edit_article(article_id):
    article = Article().find_article_by_id(article_id)

    return render_template('post-edit.html', article=article)


@admin.route('/admin/edit_draft/<int:article_id>')
def admin_edit_drafted_article(article_id):
    article = Article().find_article_by_id_and_draft(article_id)

    return render_template('post-edit.html', article=article)


# 按照文章进行分类搜索的后台接口
@admin.route('/admin/type/<sort_id>-<int:page>')
def admin_search_type(sort_id, page):
    pagesize = 50
    start = (page - 1) * pagesize
    result, total = Article().find_by_type_except_draft(start, pagesize, sort_id)
    total = ceil(total / pagesize)
    return render_template('admin.html', page=page, result=result, total=total)


# 按照文章标题进行模糊查询的后台接口
@admin.route('/admin/search/<keyword>')
def admin_search_headline(keyword):
    result = Article().find_by_headline_except_draft(keyword)
    return render_template('admin.html', page=1, result=result, total=1)


# 文章的隐藏切换接口
@admin.route('/admin/article/hide/<int:article_id>')
def admin_article_hide(article_id):
    hidden = Article().switch_hidden(article_id)
    return str(hidden)


# 文章的推荐切换接口
@admin.route('/admin/article/recommend/<int:article_id>')
def admin_article_recommend(article_id):
    recommended = Article().switch_recommended(article_id)
    return str(recommended)
