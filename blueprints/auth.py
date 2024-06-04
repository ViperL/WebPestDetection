from flask import Blueprint,render_template,request,Response,abort,session,g
from models import UserModel,ImgModel
from decorators import login_requeired
from exts import db
import string, random

bp = Blueprint("auth",__name__,url_prefix="/auth")   #蓝图名，Flask识别标号，url前缀

#----用户权限相关代码存放于此----#

#----展示登录页面----#
@bp.route('/login')
def login():
    return render_template("login.html")

#----展示注册页面
@bp.route('/register')
def register():
    return render_template("register.html")

#----展示密码修改页面----#
@bp.route('/edit')
@login_requeired
def account_edit():
    return render_template("account.html",g=g)

#----注册账号----#
@bp.route('/register',methods=["POST"])
def register_account():
    if request.method == 'POST':
        email = request.form.get("email")
        psw = request.form.get("psw")
        psw2 = request.form.get("psw2")
        if(psw!=psw2):
            return render_template("info.html",info_title="提示",messages="两次密码不相同，请检查后重试")
            #resp = Response("两次密码不相同")
            #abort(resp)
        if(UserModel.query.filter_by(email=email)==None):
            return render_template("info.html",info_title="提示",messages="邮箱已注册过，请直接登录")
            #resp = Response("邮箱已注册过，请直接登录")
            #abort(resp)
        user = UserModel(username=email,password=psw,email=email)
        db.session.add(user)
        db.session.commit()
        #resp = Response("创建成功，请进行登录")
        #abort(resp)
        return render_template("info.html",info_title="提示",messages="创建成功，请进行登录")
    else:
        return render_template("register.html")

#----登录账号----#
@bp.route('/login',methods=["POST"])
def login_account():
    if request.method == 'POST':
        account = request.form.get("account")
        psw = request.form.get("psw")
        users = UserModel.query.filter_by(username=account)
        for user in users:
            if(user.password == psw):
                # 添加cookie以保持登录状态
                session['username']=user.username
                setattr(g,'username',user.username)    #添加全局变量，用于上下文处理器
                return render_template("homepage.html")
        else:
            return render_template("info.html",info_title="提示",messages="帐号或密码错误，请检查后重新登录")
            #resp = Response("帐号或密码错误，请检查后重新登录")
            #abort(resp)
    else:
        return render_template("register.html")

#----密码修改----#
@bp.route('/edit',methods=["POST"])
def edit_account():
    if request.method == 'POST':
        pswold = request.form.get("pswold")
        psw = request.form.get("psw")
        psw2 = request.form.get("psw2")
        if(psw!=psw2):
            return render_template("info.html",info_title="提示",messages="两次密码不相同，请检查后重试")
        user = UserModel.query.filter_by(username=g.username).first()
        if(pswold==user.password):
            user.password=psw       #修改密码
            db.session.commit()
            session.clear()         #清除cookie
            return render_template("info.html",info_title="提示",messages="密码修改成功，请重新登录")
        else:
            return render_template("info.html",info_title="提示",messages="原密码不正确，请检查后重试")
    else:
        return render_template("register.html")

#----登出帐号，清除cookie----#
@bp.route('/logout')
def logout():
    session.clear()     #清除cookie
    return render_template('login.html')
