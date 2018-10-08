# 后台
from flask import Blueprint
from flask.views import  MethodView
from flask import render_template,session,g
from apps.cms.forms import (UserForm,
                            ResetPwdForm,
                            ResetEailForm,
                            ResetEmailSendCode,
                            BannerUpdate,
                            BannerForm,
                            updateboardFrom,
                            deleteboardFrom,
                            addBoaderFrom)
from flask import request,jsonify
from apps.common.baseResp import *
from ext import db,mail
from flask_mail import Message
from apps.cms.models import *
from config import REMBERME,LOGIN,CURRENT_USER_ID,CURRENT_USER
import string
import random
from apps.common.memcachedUtil import saveCache,getCache
from functools import wraps
from apps.common.models import  *
from qiniu import Auth


bp = Blueprint('cms',__name__,url_prefix="/cms")


def loginDecotor(func):
    """限制登录的装饰器"""
    @wraps(func)
    def inner(*args, **kwargs):
        login = session.get(REMBERME)
        if login == LOGIN:
            return func(*args, **kwargs)
        else:
            return render_template("cms/login.html")
    return inner


def checkPermission(permission):
    def outer(func):
        @wraps(func)
        def inner(*args,**kwargs):
            # 取出来当前的用户， 判断这个用户有没有这个权限
            userid = session[CURRENT_USER_ID]
            user = User.query.get(userid)
            r = user.checkpermission(permission)
            if r:
                return func(*args,**kwargs)
            else:
                return render_template("cms/login.html")
        return inner
    return outer

@bp.route("/")
def loginView():
    return render_template("cms/login.html")

@bp.route('/login/',methods=['post'])
def login():
    fm = UserForm(formdata=request.form)
    if fm.validate():
        email = fm.email.data # name=email的值
        pwd = fm.password.data
        user = User.query.filter(User.email == email).first()
        if not user : # 没有查询到用户
            return jsonify(respParamErr('用户名不对'))
        #if user.password == pwd : # 登陆成功
        if user.checkPwd(pwd):
            remberme = request.values.get("remberme")
            session[REMBERME] = LOGIN
            session[CURRENT_USER_ID] = user.id
            if remberme == '1' : # 前端勾选了记住我
                session.permanent=True #设置这个属性之后回去config访问过期天数，如果没有设置，默认是31天
            return jsonify(respSuccess('登陆成功'))
        else: # 密码错误
            return jsonify(respParamErr("密码错误"))
    else:
        return jsonify(respParamErr(msg=fm.err))


@bp.route('/index/')
@loginDecotor
def cms_index():
    return render_template('cms/cms_index.html')


@bp.route("/logout/")
@loginDecotor
def logout():
    session.clear()
    return render_template("cms/login.html")


@bp.route("/user_infor/")
@checkPermission(Permission.USER_INFO)
@loginDecotor
def user_infor():
    return render_template("cms/userInfo.html")


class ResetPwd(MethodView) :

    decorators = [checkPermission(Permission.USER_INFO),loginDecotor]

    def get(self):
        return render_template('cms/resetpwd.html')

    def post(self):
        fm = ResetPwdForm(formdata=request.form)
        if fm.validate():
            # 拿到原来的密码数据库查询
            userid = session[CURRENT_USER_ID]
            user = User.query.get(userid)
            r = user.checkPwd(fm.oldpwd.data)
            if r : #旧密码是对
                user.password = fm.newpwd.data
                db.session.commit()
                return jsonify(respSuccess(msg='修改成功'))
            else:
                return jsonify(respParamErr(msg='修改失败,旧密码错误'))
        else:
            return jsonify(respParamErr(msg=fm.err))
bp.add_url_rule('/resetpwd/',endpoint='resetpwd',view_func=ResetPwd.as_view('resetpwd'))

class ResetEmail(MethodView):
    # 给类视图添加装饰器
    decorators = [loginDecotor,checkPermission(Permission.USER_INFO)]
    def get(self):
        '''渲染修改邮箱的模板'''
        return render_template('cms/resetemail.html')
    def post(self):
        '''修改邮箱'''
        fm = ResetEailForm(formdata=request.form)
        if fm.validate:
            # 判断邮箱在不在
            # user = User.query.filter(User.email == fm.email.data).first()
            # if user:
            #     return jsonify(respParamErr(msg='邮箱已注册'))
            # # 判断验证码
            # emailcode = getCache(fm.email.data)
            # # upper()  不区别大小写
            # if not emailcode or emailcode != fm.emailCode.data.upper():
            #     return jsonify(respParamErr(msg='请输入正确的邮箱验证码'))
            # 修改邮箱
            user = User.query.get(session[CURRENT_USER_ID])
            user.email = fm.email.data
            db.session.commit()
            return jsonify(respSuccess(msg='修改邮箱成功'))
        else:
            return jsonify(respParamErr(msg=fm.err))

@bp.route("/send_email_code/",methods=['post'])
@loginDecotor
@checkPermission(Permission.USER_INFO)
def sendEmailCode():
    '''发送邮箱验证码'''
    fm = ResetEmailSendCode(formdata=request.form)
    if fm.validate():
        # # 查询邮箱有没有
        # user = User.query.filter(User.email == fm.email.data).first()
        # if user :
        #     return jsonify(respParamErr(msg='邮箱已注册'))
        # else:   # 发送邮件
            r = string.ascii_letters+string.digits
            r = ''.join(random.sample(r, 6))
            saveCache(fm.email.data,r.upper(),30*60)
            msg = Message("破茧科技更新邮箱验证码", recipients=[fm.email.data], body="验证码为" + r)
            mail.send(msg)
            return jsonify(respSuccess(msg='发送成功，请查看邮箱'))
    else:
        return jsonify(respParamErr(msg=fm.err))

bp.add_url_rule('/resetemail/',endpoint='resetemail',view_func=ResetEmail.as_view('resetemail'))

# 帖子管理页面
@bp.route("/showpost/")
@loginDecotor
@checkPermission(Permission.PLATE)
def showPost():
    posts = Post.query.all()
    context = {
        'posts':posts
    }
    return render_template("cms/postmgr.html",**context)
#加精
@bp.route("/addtag/",methods=['post'])
@loginDecotor
@checkPermission(Permission.PLATE)
def addTag():
    post_id = request.values.get("post_id")
    post = Post.query.filter(Post.id == post_id).first()
    if post :
        tag = Tag(post=post,status=True)
        db.session.add(tag)
        db.session.commit()
        return jsonify(respSuccess("加精完成"))
    else:
        return jsonify(respParamErr("请传入正确的post_id"))

#取消加精
@bp.route("/deletetag/",methods=['post'])
@loginDecotor
@checkPermission(Permission.PLATE)
def deleteTag():
    post_id = request.values.get("post_id")
    tag = Tag.query.filter(Tag.post_id == post_id).first()
    if tag :
        tag.status = False
        db.session.commit()
        return jsonify(respSuccess("取消加精成功"))
    else:
        return jsonify(respParamErr("请传入正确的post_id"))

@bp.route("/deletepost/",methods=['post'])
@loginDecotor
@checkPermission(Permission.BANNER)
def deletepost():
    # 拿到客户端提交的id
    post_id = request.values.get("post_id")
    board_name = request.values.get("board_name")
    # "".isdigit()
    # if not post_id or not post_id.isdigit() :
    #     return  jsonify(respParamErr(msg='请输入正确banner_id'))
    # 从数据库删除
    post = Post.query.filter(Post.id == post_id).first()
    if post :
        board = Board.query.filter(Board.boardname == board_name).first()
        board.postnum = str(int(board.postnum) - 1)
        db.session.delete(post)
        db.session.commit()
        return jsonify(respSuccess(msg='删除成功'))
    else: # 没有
        return jsonify(respParamErr(msg='请输入正确post_id'))


@bp.route("/deletecommon/",methods=['post'])
@loginDecotor
@checkPermission(Permission.BANNER)
def deletecommon():
    # 拿到客户端提交的id
    common_id = request.values.get("common_id")
    # 从数据库删除
    common = Common.query.filter(Common.id == common_id).first()
    if common :
        db.session.delete(common)
        db.session.commit()
        return jsonify(respSuccess(msg='删除成功'))
    else: # 没有
        return jsonify(respParamErr(msg='请输入正确post_id'))


# 评论管理页面
@bp.route("/common/")
@loginDecotor
@checkPermission(Permission.PLATE)
def showcommon():
    common = Common.query.all()
    context = {
        'commons':common
    }
    return render_template("cms/common.html",**context)



# 轮播图管理
@bp.route('/banner/')
@loginDecotor
@checkPermission(Permission.BANNER)
def banner_view():
     banners =  Banner.query.all()
     context = {
         'banners':banners
     }
     return render_template("cms/banner.html",**context)


# 添加轮播图
@bp.route("/addbanner/",methods=['post'])
@loginDecotor
@checkPermission(Permission.BANNER)
def addBanner():
    fm = BannerForm(formdata=request.form)
    if fm.validate():
        banner = Banner(bannerName=fm.bannerName.data,
                        imglink=fm.imglink.data,
                        link=fm.link.data,
                        priority=fm.priority.data)
        db.session.add(banner)
        db.session.commit()
        return jsonify(respSuccess(msg='添加成功'))
    else:
        return jsonify(respParamErr(msg=fm.err))

@bp.route("/deletebanner/",methods=['post'])
@loginDecotor
@checkPermission(Permission.BANNER)
def deleteBanner():
    # 拿到客户端提交的id
    banner_id = request.values.get("id")
    "".isdigit()
    if not banner_id or not banner_id.isdigit() :
        return  jsonify(respParamErr(msg='请输入正确banner_id'))
    # 从数据库删除
    banner = Banner.query.filter(Banner.id == banner_id).first()
    if banner :
        db.session.delete(banner)
        db.session.commit()
        return jsonify(respSuccess(msg='删除成功'))
    else: # 没有
        return jsonify(respParamErr(msg='请输入正确banner_id'))

@bp.route("/updatebanner/",methods=['post'])
@loginDecotor
@checkPermission(Permission.BANNER)
def updateBanner():
    fm = BannerUpdate(formdata=request.form)
    if fm.validate():
        banner = Banner.query.get(fm.id.data)
        if banner :
            banner.link = fm.link.data
            banner.imglink = fm.imglink.data
            banner.priority = fm.priority.data
            banner.bannerName = fm.bannerName.data
            db.session.commit()
            return jsonify(respSuccess(msg='更新成功'))
        else:
            return jsonify(respParamErr(msg='id失效'))
    else:
        return jsonify(respParamErr(msg=fm.err))



# 应该写common中，因为这个视图函数，前后台都要使用
# 给客户端返回上传的令牌（token），因为
@bp.route("/qiniu_token/")
def qiniukey():
    # 通过secer-key id 生成一个令牌，返回给客户端
    ak = "gixRZTC9nnM_ODSEyAmDtFPVBD5sBWJo1dsfszvB"
    sk = "X8TYRWzELi-hfyzl1MeAkEbS9i5DKL_8qI4m_o3l"
    q = Auth(ak, sk)
    bucket_name = 'pjssb' # 仓库的名字
    token = q.upload_token(bucket_name)
    return jsonify({'uptoken': token})


@bp.route("/board/")
@loginDecotor
@checkPermission(Permission.PLATE)
def board():
    board = Board.query.all()
    context = {
        'boards': board
    }
    return render_template("cms/board.html", **context)

#添加板块
@bp.route("/addboard/",methods=["post"])
@loginDecotor
@checkPermission(Permission.PLATE)
def addboard():
    fm = addBoaderFrom(formdata=request.form)
    if fm.validate():
        board = Board(boardname=fm.boardname.data)
        db.session.add(board)
        db.session.commit()
        return jsonify(respSuccess(msg='添加成功'))
    else:
        return jsonify(respParamErr(msg=fm.err))
#更新板块
@bp.route("/updateboard/",methods=["post"])
@loginDecotor
@checkPermission(Permission.PLATE)
def updateboard():
    fm  = updateboardFrom(formdata=request.form)
    if fm.validate():
        board = Board.query.filter(Board.id == fm.id.data).first()
        board.boardname = fm.boardname.data
        db.session.commit()
        return jsonify(respSuccess(msg='修改成功'))
    else:
        return jsonify(respParamErr(msg=fm.err))

#删除板块
@bp.route("/deleteboard/",methods=["post"])
@loginDecotor
@checkPermission(Permission.PLATE)
def deleteboard():
    # 拿到客户端提交的id
    board_id = request.values.get("id")
    "".isdigit()
    # if not board_id or not board_id.isdigit() :
    #     return  jsonify(respParamErr(msg='请输入正确board_id'))
    # 从数据库删除
    board = Board.query.filter(Board.id == board_id).first()
    if board :
        db.session.delete(board)
        db.session.commit()
        return jsonify(respSuccess(msg='删除成功'))
    else: # 没有
        return jsonify(respParamErr(msg='请输入正确board_id'))


# 每次请求的时候都会执行，返回字典可以直接在模板中使用
@bp.context_processor
def requestUser():
    login = session.get(REMBERME)
    if login == LOGIN:
        userid = session[CURRENT_USER_ID]
        user = User.query.get(userid)
        return {'user': user}
    return {}
