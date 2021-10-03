# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年09月27日15时
"""
from sqlalchemy import Table
from common.database import db_connect

db_session, md, DBase = db_connect()


class Sort(DBase):
    __table__ = Table('sort', md, autoload=True)
