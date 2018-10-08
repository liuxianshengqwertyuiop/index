# 前台
from flask import Blueprint,request,make_response,session
from config import FRONT_USER_ID,LOGIN,FRONT_REMBERME
from flask import render_template
from flask.views import  MethodView
from apps.front.forms import (SendSmsCodeForm,
                              SignupFrom,
                              SigninForm,
                              FindpwdFrom,
                              SendCodeForm,
                              AddPostForm)
import string
import random
from dysms_python.demo_sms_send import send_sms
from flask import jsonify
from apps.common.baseResp import *
import json
from apps.common.captcha.xtcaptcha import Captcha
from io import BytesIO
from apps.common.memcachedUtil import saveCache,delete
from apps.common.models import *
from functools import wraps
import math
from flask_paginate import Pagination,get_page_parameter
from flask import redirect
from flask import url_for

bp = Blueprint('front',__name__)



def loginDecotor(func):
    """限制登录的装饰器"""
    @wraps(func)
    def inner(*args, **kwargs):
        login = session.get(FRONT_REMBERME)
        if login == LOGIN:
            return func(*args, **kwargs)
        else:
            return render_template("front/signin.html")
    return inner

class Page:
    countofpage = 10
    @property
    def page(self): # 一共有多少页
         count = Post.query.count()
         return   math.ceil(count / self.countofpage)
    currentpage = 0 #默认是第0页
    posts = None

# @bp.route("/")
# def loginView():
#     # 查出来轮播图（4）
#     banners = Banner.query.order_by(Banner.priority.desc()).limit(2)
#     # 查出板块名
#     board = Board.query.order_by(Board.create_time.desc()).all()
#     board_id = request.args.get("boarder_id") # 可选参数
#     if board_id:  # 存在
#        posts = Post.query.filter(Post.board_id == board_id).all()
#        # count = Post.query.filter(Post.board_id == board_id).count()
#     else:  # 不存在
#        # count = Post.query.count()
#        posts = Post.query.all()
#     content = {
#         'banners': banners,
#         "boards": board,
#         'posts': posts
#     }
#     return render_template("front/index.html",**content)

@bp.route("/")
def index():
    banners = Banner.query.order_by(Banner.priority.desc()).limit(4)
    board = Board.query.all()
    board_id = request.args.get("boarder_id") # 可选参数
    # flask分页插件
    # 当前页
    page = request.args.get(get_page_parameter(), type=int, default=1)
    begin = (page - 1) * 10
    end = begin + 10
    # 按照阅读阅读量进行排序
    readCount = request.args.get("readcount", None)
    if board_id:  # 存在
       if readCount :
           tup = (Post.readCount.desc(),Post.create_time.desc())
       else:
           tup = (Post.create_time.desc())
       posts = Post.query.filter(Post.board_id == board_id).order_by(tup).slice(begin,end)
       count = Post.query.filter(Post.board_id == board_id).count()
    else:  # 不存在
        if readCount:
            posts = Post.query.order_by(Post.readCount.desc(), Post.create_time.desc()).slice(begin, end)
        else:
            posts = Post.query.order_by(Post.create_time.desc()).slice(begin, end)
            # Post.query.order_by(Post.tag.create_time.desc(),Post.create_time.des)
            # sts = Post.query.outerjoin(Tag, Post.id == Tag.post_id).order_by(Tag.create_time.desc()).all()
        count = Post.query.count()
    pagination = Pagination(bs_version=3,page=page, total=count)
    context = {
        'banners': banners,
        "boards":board,
        'posts':posts,
        #'page':page
        'pagination':pagination
    }
    return render_template("front/index.html",**context)

@bp.route('/logout/')
def logout():
    session.pop(FRONT_USER_ID)
    return redirect(url_for("front.index"))

class Signup(MethodView):
    def get(self):
        # 从那个页面点击的注册按钮  (Referer: http://127.0.0.1:9000/signin/)
        location = request.headers.get("Referer")
        if not location :  # 如果直接输入的注册的连接，location为空
            location = '/'
        context = {
            'location':location
        }
        return render_template("front/signup.html",**context)
    def post(self):
        fm = SignupFrom(formdata=request.form)
        if fm.validate():
            # 把这个用户保存到数据库中
            u = FrontUser(telephone=fm.telephone.data,
                      username=fm.username.data,
                      password=fm.password.data)
            db.session.add(u)
            db.session.commit()
            delete(fm.telephone.data) #注册成功，删除手机验证码
            return jsonify(respSuccess("注册成功，真不容易啊"))

        else:
            return jsonify(respParamErr(fm.err))
bp.add_url_rule("/signup/",endpoint='signup',view_func=Signup.as_view('signup'))


@bp.route("/send_sms_code/",methods=['post'])
def sendSMSCode():
    fm = SendSmsCodeForm(formdata=request.form)
    if fm.validate():
        #生成验证码
        h = string.digits
        h = ''.join(random.sample(h, 4))
        #发送验证码
        r = send_sms(phone_numbers=fm.telephone.data,smscode=h) #b'{"Message":"OK","RequestId":"26F47853-F6CD-486A-B3F7-7DFDCE119713","BizId":"102523637951132428^0","Code":"OK"}'
        if  json.loads(r.decode("utf-8"))['Code'] == 'OK':
            saveCache(fm.telephone.data,h,30*60)
            return jsonify(respSuccess("短信验证码发送成功，请查收"))
        else:  # 发送失败
            return jsonify(respParamErr("请检查网络"))
    else:
        return jsonify(respParamErr(fm.err))

@bp.route("/img_code/")
def ImgCode():
    # 生成6位的字符串
    # 把这个字符串放在图片上
        #  用特殊字体
        #  添加横线
        #  添加噪点
    text, img = Captcha.gene_code() # 通过工具类生成验证码
    print(text)
    out = BytesIO() # 初始化流对象
    img.save(out, 'png') # 保存成png格式
    out.seek(0)  # 从文本的开头开始读
    saveCache(text,text,5*60)
    resp = make_response(out.read()) # 根据流对象生成一个响应
    resp.content_type = "image/png" # 设置响应头中content-type
    return resp


class Signin(MethodView):
    def get(self):
        return render_template("front/signin.html")
    def post(self):
        fm = SigninForm(formdata=request.form)
        if fm.validate():
            # 通过电话查询密码
            user = FrontUser.query.filter(FrontUser.telephone == fm.telephone.data).first()
            if not  user :
                return jsonify(respParamErr("电话号未注册，请注册"))
            # 密码进行比较
            r = user.checkPwd(fm.password.data)
            if r  :
                session[FRONT_REMBERME] = LOGIN
                session[FRONT_USER_ID] = user.id
                return jsonify(respSuccess("登录成功"))
            else:
                return  jsonify(respParamErr("密码错误"))
        else:
            return jsonify(respParamErr(fm.err))

bp.add_url_rule("/signin/",endpoint='signin',view_func=Signin.as_view('signin'))



class FindPws(MethodView):
    def get(self):
        return render_template("front/findpwd.html")
    def post(self):
        fm = FindpwdFrom(formdata=request.form)
        if fm.validate():
            r = FrontUser.query.filter(FrontUser.telephone == fm.telephone.data).first()
            r.password = fm.password.data
            db.session.commit()
            return jsonify(respSuccess(msg="修改成功"))
        else:
            return jsonify(respParamErr(fm.err))

@bp.route("/sendcode/",methods=["post"])
def sendcode():
    fm =SendCodeForm(formdata=request.form)
    if fm.validate():
        rs = string.digits
        rs = ''.join(random.sample(rs, 4))
        r = send_sms(phone_numbers=fm.telephone.data,
                     smscode=rs)
# b'{"Message":"OK","RequestId":"26F47853-F6CD-486A-B3F7-7DFDCE119713","BizId":"102523637951132428^0","Code":"OK"}'

        if json.loads(r.decode("utf-8"))['Code'] == 'OK':
            saveCache(fm.telephone.data,rs,30*60)
            return jsonify(respSuccess(msg="短信验证码发送成功，请查收"))
        else:  # 发送失败
            return jsonify(respParamErr(msg="请检查网络"))
    else:
        return jsonify(respParamErr(fm.err))


class Addpost(MethodView):
    decorators = [loginDecotor]
    def get(self):
        board = Board.query.all()#desc()  .order_by(Board.create_time.desc())
        context = {
            "boards": board
        }
        return render_template("front/addpost.html",**context)
    def post(self):
        fm = AddPostForm(formdata=request.form)
        if fm.validate() :
            # 存储到数据库中
            user_id = session[FRONT_USER_ID]
            post = Post(title=fm.title.data,content=fm.content.data,
                 board_id=fm.boarder_id.data,user_id=user_id)

            board = Board.query.filter(Board.id == fm.boarder_id.data).first()
            board.postnum =str(int(board.postnum) + 1)
            # int(board.postnum) + 1
            db.session.add(post)
            db.session.commit()
            return jsonify(respSuccess("发布成功"))
        else:
            print(respParamErr(fm.err))
            return jsonify(respParamErr(fm.err))
bp.add_url_rule("/addpost/",endpoint='addpost',view_func=Addpost.as_view('addpost'))


# 展示帖子的内容
@bp.route("/showpostdetail/")
def showpostdetail():
    # 根据帖子的id查找到帖子
    post_id = request.args.get("post_id")
    if not post_id :
        return render_template("/")
    post = Post.query.filter(Post.id==post_id).first()
    if not post :
        return render_template("/")
    commons = Common.query.filter(Common.post_id == post_id).all()
    # 修改浏览量
    if post.readCount:
        post.readCount = post.readCount + 1
    else:
        post.readCount = 1
    db.session.commit()
    context = {
        'post':post,
        'commoms':commons
    }
    return render_template("front/postdetail.html",**context)

@bp.route("/addcommon/",methods=['post'])
def addCommon():
    # 判断用户有没有登录
    # 获取当前用户的id
    user_id = session.get(FRONT_USER_ID,None)
    if not user_id :
        return jsonify(respParamErr("请先登录"))
    # 获取帖子的id
    post_id = request.values.get("post_id")
    # 获取评论的内容
    content = request.values.get("content")
    if not content:
        return jsonify(respParamErr("贴子内容不能为空"))
    # 在数据库中插入
    commom = Common(content=content,post_id=post_id,user_id=user_id)
    db.session.add(commom)
    db.session.commit()
    return jsonify(respSuccess("评论成功"))

@bp.context_processor
def request_befor():
    front_user_id = session.get(FRONT_USER_ID,None)
    if front_user_id:
        user = FrontUser.query.filter(FrontUser.id == front_user_id).first()
        return {"user":user}
    else:
        return {}
#  验证码
#  在阿里云申请账号
#  申请accesskey
#  申请签名和模板
#  下载pythondemo
#  修改demo中demo_sms_send.py
#  在项目中进行调用

