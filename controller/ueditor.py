# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年10月05日23时
"""

from flask import Blueprint, render_template, request, jsonify
from time import strftime
from os import listdir

from common.utility import compress_image

ueditor = Blueprint('ueditor', __name__)


@ueditor.route('/uedit', methods=['GET', 'POST'])
def uedit():
    # ue需要请求config.json文件，请求成功说明后台接口可以正常工作
    param = request.args.get('action')  # ue要求通过action参数来判断是什么类型的请求，因此此处没有遵循RESTubful
    if request.method == 'GET' and param == 'config':
        return render_template('config.json')

    elif request.method == 'POST' and request.args.get('action') == 'uploadimage':  # 构造上传图片的接口
        f = request.files['upfile']  # 获取前端图片文件数据
        file_name = f.filename

        # 为上传来的文件生成统一的文件名
        suffix = file_name.split('.')[-1]  # 取得文件的后缀名
        new_name = strftime('%Y%m%d_%H%M%S.' + suffix)
        f.save('./resource/upload/' + new_name)  # 保存图片

        # 对图片进行压缩，按照1200像素宽度为准，并覆盖原始文件
        source = dest = './resource/upload/' + new_name
        compress_image(source, dest, 1200)

        result = {'state': 'SUCCESS', "url": f"/upload/{new_name}", 'title': file_name, 'original': file_name}  # 构造响应数据

        return jsonify(result)  # 以JSON数据格式返回响应，供前端编辑器引用

    elif request.method == 'GET' and param == 'listimage':  # 列出所有图片给前端浏览
        list = []
        file_list = listdir('./resource/upload')
        # 将所有图片构建成可访问的URL地址并添加到列表中
        for file_name in file_list:
            if file_name.lower().endswith('.png') or file_name.lower().endswith('.jpg'):
                list.append({'url': '/upload/%s' % file_name})

        # 根据listimage接口规则构建响应数据
        result = {'state': 'SUCCESS', 'list': list, 'start': 0, 'total': 50}
        return jsonify(result)
