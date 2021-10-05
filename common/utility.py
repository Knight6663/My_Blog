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

    def rand_color(self):
        """
        生成随机RGB
        :return: RBG值
        """
        red = randint(0, 255)
        green = randint(0, 255)
        blue = randint(0, 255)
        return red, green, blue

    def gen_random_text(self):
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
        code = self.gen_random_text()
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


if __name__ == '__main__':
    ImageCode().draw_verify_code()
