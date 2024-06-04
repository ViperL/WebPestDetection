#--装饰器，用于在没登录的时候进行重定向
from functools import wraps
from flask import redirect,url_for,g

def login_requeired(func):
    @wraps(func)        #保留原函数信息
    def inner(*args,**kwargs):
        if g.username:
            return func(*args,**kwargs)
        else:
            return redirect(url_for('auth.login'))
    return inner
