from flask import Blueprint,render_template,g,request,redirect,url_for,send_file,current_app
import time,os
from decorators import login_requeired
from models import UserModel,ImgModel
from exts import db,basedir
#----引入神经网络包
from webpred import webpred as pred
#----多线程
import threading

bp = Blueprint("anayer",__name__,url_prefix="/")   #蓝图名，Flask识别标号，url前缀

#图像分析相关的代码存放在这里
#----主页----#
@bp.route('/')
@login_requeired
def homepage():
    return render_template("homepage.html",g=g)

#----展示图片上传页面----#
@bp.route('/uploader')
@login_requeired
def uploader():
    return render_template("uploader.html",g=g)

#----展示图片上传页面----#
@bp.route('/database')
@login_requeired
def database():
    user = UserModel.query.filter_by(username=g.username).first()  #由于用户名为邮箱且唯一，所以可以代id
    return render_template("database.html",g=g,imgs=user.Imgs)

#----展示图片详情----#
@bp.route('/detall',methods=["GET"])
@login_requeired
def imgdetall():
    if request.method=="GET":
        filename = request.args.get("name")
        showname = request.args.get("orgname")
        clsResult = str(ImgModel.query.filter_by(newname=filename).first().clsResult)
        clsResults = clsResult.split('\n')
        return render_template("detall.html",g=g,imgname = filename,showname=showname,clsResults=clsResults)

#----关于页----#
@bp.route('/about')
def about():
    return render_template("info.html",info_title="关于",messages="本软件基于flask和pytorch设计，用于在线害虫识别，由viperl1于2023.1.1设计")


#----上传图片----#
@bp.route('/uploader',methods=["POST"])
@login_requeired
def upader_post():
    if request.method == 'POST':
        #----获取用户id，用于标记图片
        user = UserModel.query.filter_by(username=g.username).first()  #由于用户名为邮箱且唯一，所以可以代id
        index=0         #用于计数
        processid = str(int(time.time()))               #任务组id
        for img in request.files.getlist('photo'):
            suffix = '.' + img.filename.split('.')[-1] # 获取文件后缀名
            tempfilename = str(int(time.time())) +'_p'+str(index) + suffix  #服务器中文件名
            img_path = './static/uploads/' + tempfilename # 拼接路径
            img.save(img_path) #保存图片
            
            #----创建数据库对象并写入
            imgobj = ImgModel(orgname=img.filename,tempname=tempfilename,processid=processid)
            imgobj.ownerid = user.id
            db.session.add(imgobj)
            db.session.commit()
            index = index + 1

        #----调用神经网络
        app = current_app._get_current_object()     #传递flask参数
        backThreader = threading.Thread(target=NerSelect,args=(processid,app))
        backThreader.daemon=True                    #开启守护进程
        backThreader.start()                        #开启进程
            
    return redirect(url_for('anayer.homepage'))

#----后台调用神经网络----#
def NerSelect(processid,app):
    with app.app_context():
        imgobjs = ImgModel.query.filter_by(processid=processid)
        for imgobj in imgobjs:
            #----调用神经网络
            try:
                completedname,clsResult = pred('static/uploads/'+imgobj.tempname,'static/results',imgobj.tempname)
                print("神经网络识别成功:"+completedname)
                imgobj.newname=completedname
                imgobj.clsResult = clsResult
                db.session.commit()
            except Exception as err:
                print("网络调用失败:{}".format(str(err)))
                continue


#----下载图片----#
@bp.route('/download',methods=['GET'])
@login_requeired
def download_file():
    if request.method=="GET":
        filename = request.args.get("name")
        path = basedir+'\\static\\results\\'+filename
        return send_file(path,as_attachment=True)
    else:
        return render_template("info.html",info_title="提示",messages="非法访问")
