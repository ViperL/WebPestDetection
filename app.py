from flask import Flask,request,render_template,redirect,g,session    #引入flask相关的控件
import config
from exts import db
from blueprints.auth import bp as authbp
from blueprints.anayer import bp as anayerbp
from models import UserModel
from flask_migrate import Migrate
import os


app = Flask(__name__)

#----初始化----#
app.config.from_object(config)      #由config.py初始化
#----对象绑定----#
db.init_app(app)
#----初始化迁移脚本----#
migrate = Migrate(app,db)

#----蓝图绑定----#
app.register_blueprint(authbp)
app.register_blueprint(anayerbp)

#----上下文处理器----#
@app.context_processor
def push_user_name():
    return {'username':g.username}

#----钩子函数，用来从session中获取user_id
@app.before_request
def get_user_name():
    username = session.get('username')
    if username:
        user = UserModel.query.get(username)
        setattr(g,"username",username)
    else:
        setattr(g,"username",None)  #为保证程序不出错，将帐号先设置为空

if __name__ == "__main__":
    app.run(debug=True)