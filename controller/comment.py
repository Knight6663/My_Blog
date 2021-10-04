# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年10月03日23时
"""

from flask import Blueprint, request

from module.article import Article
from module.comment import Comment

comment = Blueprint('comment', __name__)


@comment.route('/comment', methods=['POST'])
def add():
    article_id = request.form.get('article_id')
    content = request.form.get('content').strip()
    nickname = request.form.get('nickname').strip()
    ip_address = request.remote_addr

    # 对评论内容进行简单的校验
    if len(content) < 5 or len(content) > 200:
        return 'content-invalid'

    comment = Comment()
    if not comment.check_limit_per_5():
        try:
            comment.insert_comment(article_id, content, nickname, ip_address)

            Article().upadte_reply_count(article_id)  # 评论成功后，更新文章回复数量
            return 'add-pass'
        except:
            return 'add-fail'
    else:
        return 'add-limit'
