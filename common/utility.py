# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年10月02日14时
"""
from io import BytesIO
from random import sample, randint
from string import ascii_letters, digits
from PIL import Image, ImageFont, ImageDraw


class ImageCode:
    """
    生成图片验证码
    """

    def rand_color(self):
        """
        生成随机RGB
        :return: RBG值
        """
        red = randint(0, 255)
        green = randint(0, 255)
        blue = randint(0, 255)
        return red, green, blue

    def get_random_text(self):
        """
        使用sample在一个列表或字符串中，随机获取N哥字符，构建一个随机的字符列表
        :return:一个长度为4的随机字符串
        """
        ls = sample(ascii_letters + digits, 4)
        return ''.join(ls)

    def draw_interfere_lines(self, draw, num, width, height):
        """
        在图片中增加一点干扰线条
        :param draw: PIL中的ImageDraw对象
        :param num: 增加的线条数量
        :param width: 宽
        :param height: 高
        :return:
        """
        for num in range(num):
            x1 = randint(0, width / 2)
            y1 = randint(0, height / 2)
            x2 = randint(0, width)
            y2 = randint(height / 2, height)
            draw.line(((x1, y1), (x2, y2)), fill=self.rand_color(), width=2)

    def draw_verify_code(self):
        """
        绘制验证码图片
        :return:
        """
        code = self.get_random_text()
        width, height = 120, 50  # 设定图片大小，可根据实际需求调整
        im = Image.new('RGB', (width, height), 'white')  # 创建图片对象，并设定背景色为白色
        font = ImageFont.truetype(font='arial.ttf', size=40)  # 选择使用何种字体及字体大小
        draw = ImageDraw.Draw(im)  # 新建ImageDraw对象
        for i in range(4):  # 绘制字符串
            draw.text((5 + randint(-3, 3) + 23 * i, 5 + randint(-3, 3)),
                      text=code[i], fill=self.rand_color(), font=font)
        self.draw_interfere_lines(draw, 3, width, height)  # 绘制干扰线
        # im.show()  # 调试使用，可将生成的图片直接显示出来
        return im, code

    def get_code(self):
        """
        生成图片验证码并返回给控制器
        :return:
        """
        image, code = self.draw_verify_code()
        buf = BytesIO()  # 二进制形式储存，只将其存在内存中
        image.save(buf, 'jpeg')
        bstring = buf.getvalue()
        buf.close()
        return code, bstring


def model_list(result):
    """
    将单个模型类转换为标准的Python List数据
    :param result:需要转换的数据
    :return:转换好了的list,格式为:[{},{},{}]
    """
    list = []
    for row in result:
        dict = {}
        for k, v in row.__dict__.items():
            if not k.startswith('_sa_instance_state'):
                dict[k] = v
        list.append(dict)
    return list


def model_join_list(result):
    """
    将多个模型类转换为标准的Python List数据 (用于处理多表连接的数据)
    :param result: 需要转换的数据
    :return: 转换好了的list,格式为:[{},{},{}]
    """
    list = []  # 定义列表用于存放所有行
    for obj1, obj2 in result:
        dict = {}
        for k1, v1 in obj1.__dict__.items():
            if not k1.startswith('_sa_instance_state'):
                if not k1 in dict:  # 如果字典中已经存在相同的Key则跳过
                    dict[k1] = v1
        for k2, v2 in obj2.__dict__.items():
            if not k2.startswith('_sa_instance_state'):
                if not k2 in dict:  # 如果字典中已经存在相同的Key则跳过
                    dict[k2] = v2
        list.append(dict)
    return list


def compress_image(source, dest, width):
    """
    对图片进行压缩
    :param source: 文件源地址
    :param dest: 处理后文件地址
    :param width: 指定图片压缩后的大小
    :return: None
    """
    # 如果图片宽度大于1200，则调整为1200的宽度
    image = Image.open(source)
    x, y = image.size  # 获取源图片的宽和高
    if x > width:
        ys = int(y * width / x)
        xs = width  # 等比例缩放
        temp = image.resize((xs, ys), Image.ANTIALIAS)  # 调整当前图片的尺寸（同时也会压缩大小）
        temp.save(dest, quality=80)  # 将图片保存并使用80%的质量进行压缩
    else:  # 如果尺寸小于指定宽度则不缩减尺寸，只压缩保存
        image.save(dest, quality=80)


def parse_image_url(content):
    """
    解析文章内容中的图片地址，将图片url地址提取出来
    :param content:生成的文章html代码
    :return:图片url地址，list类型
    """
    from re import findall
    temp_list = findall('<img src="(.+?)"', content)  # 只对匹配到的第一个对象进行处理
    url_list = []
    for url in temp_list:
        if url.lower().endswith('.gif'):  # 如果图片类型为gif，不对其作任何处理
            continue
        url_list.append(url)
    return url_list


def download_image(url, dest):
    """
    远程下载指定URL地址的图片，并保存到临时目录中
    :param url: 需要下载的url地址
    :param dest: 保存的地址
    :return: None
    """
    from requests import get
    response = get(url)  # 获取图片的响应
    # 将图片以二进制方式保存到指定文件中
    with open(file=dest, mode='wb') as file:
        file.write(response.content)


def generate_thumb(url_list):
    """
    解析列表中的图片URL地址并生成缩略图
    :param url_list:
    :return: 缩略图名称
    """
    # 根据URL地址解析出其文件名和域名
    # 这里使用文章内容中的第一张图片来生成缩略图
    for url in url_list:  # 先遍历url_list，查找里面是否存在本地上传图片
        if url.startswith('/upload/'):
            filename = url.split('/')[-1]
            # 找到本地图片后对其进行压缩处理，设置缩略图宽度为400像素即可
            compress_image('./resource/upload/' + filename,
                           './resource/thumb/' + filename, 400)
            return filename  # 返回当前图片的文件名

    # 如果在内容中没有找到本地图片，则需要先将网络图片下载到本地再处理
    # 直接将第一张图片作为缩略图，并生成基于时间戳的标准文件名
    from time import strftime
    url = url_list[0]
    filename = url.split('/')[-1]
    suffix = filename.split('.')[-1]  # 取得文件的后缀名
    thumb_name = strftime('%Y%m%d_%H%M%S.' + suffix)
    download_image(url, './resource/download/' + thumb_name)
    compress_image('./resource/download/' + thumb_name, './resource/thumb/' + thumb_name, 400)

    return thumb_name  # 返回当前缩略图的文件名
