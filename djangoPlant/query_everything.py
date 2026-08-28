from. import logger,requests
from.publicDef import publicDef

HOSTS_URI = 'http://msr.jtscprod.com'  # 生产
HOSTS_URI_test = 'http://msr.jiatuitest.com'  # 测试
HOSTS_URI_prod = 'http://msr.jtscprod.com'  # 生产
t = 'test'
jcc = 'jt_company_center'

_qe_pdef = None
def _get_pdef():
    global _qe_pdef
    if _qe_pdef is None: _qe_pdef = publicDef()
    return _qe_pdef

def gct():
    return _get_pdef().getctime()

class queryEverything():
    def __init__(self):
        pass

    def query_jiatuiYuE(self):
        short_uri = '/ai-retail-store/agent/referral/account/bff/withdraw/balance' #预充值模式查看余额
        query_balance = HOSTS_URI + short_uri
        print(query_balance)
        req_json = ''
        res = requests.post(query_balance, json=req_json, timeout=30)
        print(_get_pdef().logcss(gct(),"【query_everything-query_jiatuiYuE】"),f"【查询加推总账户余额】:{short_uri}, 入参: {req_json}, 返回数据: {res.json()}")
        # return res.json()
        if res.json()['code'] == 0:
            ye = res.json()['data']['balance']
            # ye = 500.55
            s=str(ye).split('.') #截取小数点前后数据，s[0]为小数点前面的数值，s[1]为小数点后面的数值
            if float(s[1])==0: #判断小数点后的值是否等于0，等于0则是整数
                rs = s[0]
                print('【00000000】',rs)
            else :
                rs = ye
        else:
            rs = 0
        return str(rs)

    def query_companyId(self, login_name, env="prod"):
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        short_uri = '/company-center/center/company/info/login/name' #根据登陆账号查询企业基本信息
        query_companyId = HOSTS_URI + short_uri + '?loginName=%s' %login_name
        req_json = ''
        res = requests.get(query_companyId, json=req_json, timeout=30)
        # print('【修改企业打款方式】: ',res.json())
        print(_get_pdef().logcss(gct(),"【query_everything-query_companyId】"),f"【登录账号查询企业ID】:{query_companyId}, 入参: {req_json}, 返回数据: {res.json()}")
        return res.json()

    def query_companyInfoByCompanyId(self, companyId, env="prod"):
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        short_uri = f'/company-center/center/company/info?companyId={companyId}' #根据企业id查询企业信息
        uri = HOSTS_URI + short_uri
        req_json = ''
        res = requests.get(uri, json=req_json, timeout=30)
        # print('【修改企业打款方式】: ',res.json())
        print(_get_pdef().logcss(gct(),"【query_everything-query_companyInfoByCompanyId】"),f"【根据企业ID查询企业信息】:{uri}, 入参: {req_json}, 返回数据: {res.json()}")
        return res.json()

    def query_cropId(self, company_id):
        short_uri = '/wxauth/wxapi/corpId/get' #查询企业微信ID
        query_cropId = HOSTS_URI + short_uri + '?companyId=%s' %company_id
        req_json = ''
        res = requests.get(query_cropId, json=req_json, timeout=30)
        # print('【修改企业打款方式】: ',res.json())
        print(_get_pdef().logcss(gct(),"【query_everything-query_cropId】"),f"【查询企微ID】:{short_uri}, 入参: {req_json}, 返回数据: {res.json()}")
        return res.json()
    
    def openCorpId(self,corpId):
        #根据明文的corpId获取加密corpId
        getopencorpid = "/wxauth/wxapi/toOpenCorpId" #获取加密corpId
        short_uri = getopencorpid + "?corpId=%s"%corpId
        full_uri = HOSTS_URI+short_uri
        req_json = ""
        res = requests.post(full_uri, json=req_json, timeout=30)
        print(_get_pdef().logcss(gct(),"【query_everything-query_cropId】"),f"【根据明文的corpId获取加密corpId】:{full_uri}, 入参: {req_json}, 返回数据: {res.json()}")
        return res.json()

    def query_corpAuth(self,companyId,env='prod'):
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        short_uri ='/wxauth/wxauth/corp-manager/auth/check' #查询公众号小程序绑定情况
        query_ca = HOSTS_URI + short_uri
        req_json = ''
        header = {
            "i-companyId": companyId
        }
        res = requests.get(query_ca, headers= header, json=req_json, timeout=30)
        print(_get_pdef().logcss(gct(),"【query_everything-query_corpAuth】"),f'【查询公众号小程序绑定情况】:{short_uri}, 入参: {req_json}, 返回数据: {res.json()}')  #0是未安装，1是已安装，2是加推授权
        return res.json()
    
    def query_authAppList(self,companyId,env='prod'):
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        short_uri ='/wxauth/agent/authAppList' #查询企业已授权的企微应用
        query_ca = HOSTS_URI + short_uri
        req_json = ''
        header = {
            "i-companyId": companyId
        }
        res = requests.get(query_ca, headers= header, json=req_json, timeout=30)
        print(_get_pdef().logcss(gct(),"【query_everything-query_authAppList】"),f'【查询企业已授权的企微应用】:{short_uri}, 入参: {req_json}, 返回数据: {res.json()}')  #1是已安装，0是未安装
        return res.json()

    def selfcreated_configSave(self,companyId,corpId):
        short_uri = '/wxauth/selfcreated/config/save' #绑定企业和企微加密corpid
        sc_cs = HOSTS_URI + short_uri
        req_json = {
            "companyId": companyId,
            "corpId": corpId
            }
        res = requests.post(sc_cs, json=req_json, timeout=30)
        # print('【修改企业打款方式】: ',res.json())
        print(_get_pdef().logcss(gct(),"【query_everything-selfcreated_configSave】"),f'【绑定企业和企微加密corpid】:{short_uri}, 入参: {req_json}, 返回数据: {res.json()}')
        return res.json()
    
    def privacy_setting(self,companyId):
        short_uri = '/company-center/company-center/company/privacy_setting?companyId=%s'%companyId #配置隐私保护
        priv_set = HOSTS_URI + short_uri
        req_json = ''
        try:
            res = requests.post(priv_set, json=req_json, timeout=30)
            rlt = res.json()
        except Exception as e:
            rlt = {"code":10001, "msg":e, "data":""}
        # print('【修改企业打款方式】: ',res.json())
        print(_get_pdef().logcss(gct(),"【query_everything-privacy_setting】"),f'【配置隐私保护】:{short_uri}, 入参: {req_json}, 返回数据: {rlt}')
        return rlt

    def dzapplet_config_save(self, companyId, corpId, secretKey, t, env):
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        short_uri = '/wxauth/openwx/partner/applet/config/save' #定制化/招商版小程序配置保存
        priv_set = HOSTS_URI + short_uri
        if t == 'zs': #招商版
            req_json = {
                "companyId": companyId,
                "corpId": corpId, #小程序appid
                "secret": secretKey, #小程序secretKey
                "appType":"cpe_investment_applet"
            }
        # elif t == 'tg':  #推广版
        #     # priv_set = HOSTS_URI + '/wxauth/openwx/partner/applet/config/save'
        #     req_json = {
        #         "companyId": companyId,
        #         "corpId": corpId, #小程序appid
        #         "secret": secretKey, #小程序secretKey
        #         "appType":"cpe_popularize_applet"
        #     }
        elif t == 'dz':  #转介绍
            req_json = {
                "companyId": companyId,
                "corpId": corpId, #小程序appid
                "secret": secretKey #小程序secretKey
            }
        print(_get_pdef().logcss(gct(),"【query_everything-privacy_setting】"),f'【定制化/招商版小程序配置保存】:{priv_set}, 入参: {req_json}')
        res = requests.post(priv_set, json=req_json, timeout=30)
        # print(_get_pdef().logcss(gct(),"【query_everything-privacy_setting】"),f'【定制化/招商版小程序配置保存】:{priv_set}, 入参: {req_json}, 返回数据: {res.json()}')
        return res.json()
        
    def companyId_length(self, companyId):
        if len(companyId) >= 18:
            return True
        elif len(companyId) < 18:
            return False

