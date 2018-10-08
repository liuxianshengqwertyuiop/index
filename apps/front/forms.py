from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField
from wtforms.validators import Regexp,InputRequired,Length,EqualTo
import hashlib
from apps.front.models import FrontUser
from apps.common.memcachedUtil import getCache
from wtforms.validators import ValidationError

class BaseForm(FlaskForm):
    @property    # 把函数变成了属性来调用
    def err(self):
        return self.errors.popitem()[1][0]

class SendSmsCodeForm(BaseForm):
    telephone = StringField(validators=[Regexp('^1[35786]\d{9}$', message='请输入正确电话号码')])
    sign = StringField(validators=[InputRequired(message="必须输入签名")])

    def validate_telephone(self, filed):  # 如果手机号重复没必要发送验证码
        u = FrontUser.query.filter(FrontUser.telephone == filed.data).first()
        if u:
            raise ValidationError('手机号已被注册')

    def validate_sign(self, filed):
        # 生成md5字符串
        sign = md5(self.telephone.data)
        if sign != filed.data:
            raise ValidationError('请输入正确的签名')


class SignupFrom(SendSmsCodeForm):
    username = StringField(validators=[InputRequired(message="必须输入用户名"), Length(min=6, max=20, message="用户名必须是6-20位")])
    password = StringField(validators=[InputRequired(message="必须输入密码"), Length(min=6, max=20, message="密码必须是6-20位")])
    password1 = StringField(validators=[EqualTo('password', message="两次密码必须一致")])
    smscode = StringField(validators=[InputRequired(message="必须输入手机验证码")])
    captchacode = StringField(validators=[InputRequired(message="必须输入图片验证码")])

    sign = StringField()
    def validate_sign(self, filed):
        pass

    def validate_smscode(self, filed):
        # 从缓存中获取到，然后校验
        smscode = getCache(self.telephone.data)
        if not smscode:
            raise ValidationError('请输入正确的手机验证码')
        if smscode.upper() != filed.data:
            raise ValidationError('请输入正确的手机验证码')

    def validate_captchacode(self, filed):
        # 从缓存中获取到，然后校验
        if not getCache(filed.data):
            raise ValidationError('请输入正确的图片验证码')

    def validate_username(self, field):
        u = FrontUser.query.filter(FrontUser.username == field.data).first()
        if u:
            raise ValidationError('用户名已存在')

class SigninForm(BaseForm):
    telephone = StringField(validators=[Regexp('^1[35786]\d{9}$', message='请输入正确电话号码')])
    password = StringField(validators=[InputRequired(message="必须输入密码"),Length(min=6,max=20,message="密码必须是6-20位")])

class SendCodeForm(BaseForm):
    telephone = StringField(validators=[Regexp('^1[35786]\d{9}$',message='请输入正确电话号码')])
    def validate_telephone(self,filed):
        r = FrontUser.query.filter(FrontUser.telephone == filed.data).first()
        if not r :
            raise ValidationError('手机号未被注册')

class FindpwdFrom(SendCodeForm):
    password = StringField(validators=[InputRequired(message="必须输入密码"), Length(min=6, max=20, message="密码必须是6-20位")])
    password1 = StringField(validators=[EqualTo('password', message="两次密码必须一致")])
    smscode = StringField(validators=[InputRequired(message="必须输入手机验证码")])
    def validate_smscode(self,filed):
        # 从缓存中获取到，然后校验
        smscode = getCache(self.telephone.data)
        print("校验得到的验证码"+smscode)
        if not smscode :
            raise ValidationError('请输入正确的手机验证码')
        if smscode.upper() != filed.data :
            raise ValidationError('验证码错误')


# pjkj进行
def md5(telephone):
    m = hashlib.md5()
    v = telephone + 'zhanghendenvpengyou'
    m.update(v.encode("utf-8"))
    r = m.hexdigest()
    return r

class AddPostForm(BaseForm):
    title = StringField(InputRequired(message="帖子标题不能为空"))
    boarder_id = IntegerField(InputRequired(message="板块不能为空"))
    content = StringField(InputRequired(message="帖子内容不能为空"))
