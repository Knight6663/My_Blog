# -*- coding:UTF-8 -*-
"""
作者:吕瑞承
日期:2021年09月27日07时
"""
from sqlalchemy import MetaData


def db_connect():
    from main import db
    Session = db.sessionmaker()
    db_session = Session()
    DBase = db.Model
    metadata = MetaData(bind=db.engine)
    return db_session, metadata, DBase
