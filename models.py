from exts import db
from datetime import datetime

class UserModel(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)          #用户ID
    username = db.Column(db.String(100),nullable=False)                     #用户名
    password = db.Column(db.String(100),nullable=False)                     #密码
    email = db.Column(db.String(100),nullable=False,unique=True)            #邮箱
    join_time = db.Column(db.DateTime,default=datetime.now,nullable=False)  #加入时间

class ImgModel(db.Model):
    __tablename__="img"
    imgid = db.Column(db.Integer,primary_key=True,autoincrement=True)       #图像ID
    orgname = db.Column(db.String(100),nullable=False)                      #原始的图像名
    tempname = db.Column(db.String(100),nullable=False)                     #上传时的图像名
    newname = db.Column(db.String(100),nullable=True)                       #处理后的图像名
    clsResult = db.Column(db.String(1000),nullable=True)                  #分类详情
    processid = db.Column(db.String(100),nullable=True)                     #任务组编号，用于执行后台识别任务
    #----外键，图像拥有者
    ownerid = db.Column(db.Integer,db.ForeignKey("user.id"))
    owner = db.relationship('UserModel',backref="Imgs")                          #反向引用