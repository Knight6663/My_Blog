# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年10月03日23时
"""

from flask import Blueprint, request

from module.article import Article
from module.comment import Comment
from module.opinion import Opinion

comment = Blueprint('comment', __name__)


@comment.route('/comment', methods=['POST'])
def add():
    article_id = request.form.get('article_id')
    content = request.form.get('content').strip()
    nickname = request.form.get('nickname').strip()
    ip_address = request.remote_addr

    # 对评论内容进行简单的校验
    if len(content) < 5 or len(content) > 300:
        return 'content-invalid'

    comment = Comment()
    if not comment.check_limit_per_5():
        try:
            comment.insert_comment(article_id=article_id, content=content, nickname=nickname, ip_address=ip_address)

            Article().update_reply_count(article_id)  # 评论成功后，更新文章回复数量
            return 'add-pass'
        except:
            return 'add-fail'
    else:
        return 'add-limit'


@comment.route('/reply', methods=['POST'])
def reply():
    article_id = request.form.get('article_id')
    comment_id = request.form.get('comment_id')
    nickname = request.form.get('nickname').strip()
    content = request.form.get('content').strip()
    ip_address = request.remote_addr

    # 如果评论的字数低于5个或多于300个，均视为不合法
    if len(content) < 5 or len(content) > 300:
        return 'content-invalid'

    comment = Comment()
    # 没有超出限制才能发表评论
    if not comment.check_limit_per_5():
        try:
            comment.insert_reply(article_id=article_id, comment_id=comment_id, content=content, nickname=nickname,
                                 ip_address=ip_address)
            # 评论成功后，同步更新article表回复数

            Article().update_reply_count(article_id)
            return 'reply-pass'
        except:
            return 'reply-fail'
    else:
        return 'reply-limit'


@comment.route('/opinion', methods=['POST'])
def do_opinion():
    comment_id = request.form.get('comment_id')
    opinion_type = int(request.form.get('type'))
    ip_address = request.remote_addr

    opinion = Opinion()
    is_checked = opinion.check_opinion(comment_id, ip_address)
    if is_checked:   # 判断是否以及点赞
        return 'already-opinion'
    else:
        opinion.insert_opinion(comment_id, opinion_type, ip_address)
        Comment().update_by_opinion(comment_id, opinion_type)
        return 'opinion-pass'
