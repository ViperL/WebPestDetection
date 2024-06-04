from flask_sqlalchemy import SQLAlchemy
import os

#对象引用库
db = SQLAlchemy()            #创建db对象

#项目的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))