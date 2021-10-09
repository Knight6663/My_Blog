# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年10月02日23时
"""
from os import listdir, remove

from flask import Blueprint, render_template, abort, request, session

from common.utility import parse_image_url, generate_thumb
from module.article import Article
from module.comment import Comment
from module.users import Users

article = Blueprint('article', __name__)


@article.route('/article/<int:article_id>')
def read(article_id):
    try:
        article_result = Article().find_article_and_user_by_id(article_id)
        if article_result is None:
            abort(404)
    except:
        abort(500)

    Article().updata_read_count(article_id)  # 该文章阅读次数加1
    prev_next = Article().find_prev_and_next_by_id(article_id)  # 根据当前文章id查询上一篇和下一篇文章

    comment_list = Comment().get_comment_list(article_id, 0, 20)  # 显示当前文章的评论

    return render_template('article.html', article_result=article_result, prev_next=prev_next,
                           comment_list=comment_list)


@article.route('/prepost')
def pre_post():
    return render_template('post.html')


@article.route('/article', methods=['POST'])
def add_article():
    headline = request.form.get('headline')
    content = request.form.get('content')
    sort_id = int(request.form.get('sort_id'))
    drafted = int(request.form.get('drafted'))
    article_id = int(request.form.get('article_id'))

    if session.get('user_id') is None:
        return 'perm-denied'
    else:
        user = Users().find_by_userid(session.get('user_id'))

        if user:    # 判断这个user_id是否在数据库内，不存在就不允许发布文章
            # 首先为文章生成缩略图，优先从内容中找，找不到则随机生成一张
            url_list = parse_image_url(content)
            if len(url_list) > 0:   # 表示文章中存在图片
                thumbname = generate_thumb(url_list)
            else:
                # 如果文章中没有图片，则根据文章类别指定一张缩略图
                thumbname = '%d.png' % sort_id

            article = Article()
            if article_id == 0:    # 判断article_id是否为0，如果为0则表示是新数据
                try:
                    id = article.insert_article(sort_id=sort_id, headline=headline, content=content,
                                                thumbnail=thumbname, drafted=drafted)

                    # 新增文章成功后，将已经静态化的文章列表页面全部删除，便于生成新的静态文件
                    index_static_file = listdir('./template/index-static/')
                    for file in index_static_file:
                        remove('./template/index-static/' + file)

                    return str(id)
                except Exception as e:
                    return 'post-fail'
            else:   # 如果是已经添加过的文章，则做更新操作
                try:
                    id = article.update_article(article_id=article_id, sort_id=sort_id,
                                                headline=headline, content=content,
                                                thumbnail=thumbname, drafted=drafted)
                    return str(id)
                except:
                    return 'post-fail'
        else:
            return 'perm-denied'
