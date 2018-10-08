class BaseResp:
    def __init__(self,code,msg,data=None):
        self.data = data
        self.code = code
        self.msg = msg

class respCode:
    SUCCESS = 200  # 成功
    UNAUTHERROR = 401  # 没有权限
    PARAMERR= 402 # 参数错误

# 成功的返回
def respSuccess(msg,data=None):
    return BaseResp(code=respCode.SUCCESS,msg=msg,data=data).__dict__

def respParamErr(msg='参数错误',data=None):
    return BaseResp(code=respCode.PARAMERR,msg=msg,data=data).__dict__

def respUnAutherr(msg='没有访问权限'):
    return BaseResp(code=respCode.UNAUTHERROR,msg=msg).__dict__



#if __name__ == '__main__':
#    print(BaseResp(code=respCode.PARAMERR,msg='成功',data=None).__dict__)





