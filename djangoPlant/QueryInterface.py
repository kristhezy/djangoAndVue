#查询接口
from. import requests,datetime,logger
from.publicDef import publicDef

_pdef = None
def _get_pdef():
    global _pdef
    if _pdef is None: _pdef = publicDef()
    return _pdef

HOSTS_URI_test = 'http://msr.jiatuitest.com'  # 测试
HOSTS_URI_prod = 'http://msr.jtscprod.com'  # 生产
HOSTS_URI_ydtest = 'http://test.msr.jt.adenfin.com'  # 亚丁测试
HOSTS_URI_hmzx = 'http://test.msr.jt.changfeng666.com' #亚丁线索顾问平台
HOSTS_URI_nxlt = 'http://msr.qzds.nxunicom.local'  # 宁夏联通

def gct():
    return _get_pdef().getctime()

class QueryInterface():
    def __init__(self):
        self.query_module = "/company-center/company-center/company/module/bycompany"  #查询公司功能模块列表
        self.query_info = "/company-center/center/company/info"  #查询企业基本信息
        self.query_payment = "/company-center/company-center/company/payment/info"  #查询企业的打款方式
        self.query_cardListInfo = "/company-center/center/company/card/batch/list" #批量查询人员基本信息
        self.query_gatewayGCI = '/config/gatewayzuul/default' #查询网关灰度企业
        self.query_userinfo = '/usercenter/center/user/' #查找用户信息
        self.query_userinfobycomphone ='/usercenter/center/user/info/phone' #根据phone和companyId查询用户信息
        self.query_pidbycidat = '/ai-retail-store/retail/partner/findByCompanyIdAndTel' #根据企业ID和手机号查询推荐官信息

    #获取接口域名
    def getUri(self,env):
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        elif env == 'ydtest':
            HOSTS_URI = HOSTS_URI_ydtest
        elif env == 'hmzx':
            HOSTS_URI = HOSTS_URI_hmzx
        elif env == 'nxlt':
            HOSTS_URI = HOSTS_URI_nxlt
        return HOSTS_URI

    def query_companyModule(self,company_id,env):
        #查询公司功能模块列表
        HOSTS_URI = self.getUri(env)
        query_rui = HOSTS_URI+self.query_module
        req_json = {
            "companyId": company_id
        }
        res = requests.post(query_rui, json=req_json, timeout=30)
        if res.status_code == 200:
            logger.info('【QueryInterface-query_companyModule】查询企业开通模块: %s, 入参: %s, 返回数据: %s', self.query_module, req_json, res.json())
            return res.json()
        else:
            logger.error('【QueryInterface-query_companyModule】查询企业模块接口异常: %s', res)
            return ""

    def query_companyInfo(self, company_id, env):
        #查询企业基本信息
        HOSTS_URI = self.getUri(env)
        query_rui = HOSTS_URI + self.query_info + '?companyId=%s' %company_id
        req_json = ''
        res = requests.get(query_rui, json=req_json, timeout=30)
        if res.status_code == 200:
            logger.info('【QueryInterface-query_companyInfo】查询企业信息: %s, 入参: %s, 返回数据: %s', query_rui, req_json, res.json())
            return res.json()
        else:
            logger.error('【QueryInterface-query_companyInfo】查询企业基本信息接口异常: %s', res)
            return ""

    def query_companyPayment(self, company_id, env):
        #查询企业的打款方式
        HOSTS_URI = self.getUri(env)
        query_rui = HOSTS_URI+self.query_payment
        req_json = {
            "companyId": company_id
        }
        res = requests.post(query_rui, json=req_json, timeout=30)
        logger.info('【QueryInterface-query_companyPayment】查询企业打款方式: %s, 入参: %s, 返回数据: %s', self.query_payment, req_json, res.json())
        return res.json()

    def query_cardInfo(self, card_ids, env):
        #批量查询企业的员工信息
        HOSTS_URI = self.getUri(env)
        query_rui = HOSTS_URI+self.query_cardListInfo
        req_json = card_ids
        res = requests.post(query_rui, json=req_json, timeout=30)
        # print('【批量查询人员基本信息】:%s, 入参: %s, 返回数据: %s' %(self.query_cardListInfo,req_json,res.json()))
        logger.info('【QueryInterface-query_cardInfo】批量查询人员基本信息: %s, 入参: %s, 返回数据: %s', self.query_cardListInfo, req_json, res.json())
        return res.json()

    def query_grayCompany(self,env):
        #查询灰度企业
        HOSTS_URI = self.getUri(env)
        query_gc = HOSTS_URI + self.query_gatewayGCI
        header = {
            "Authorization": "Basic bXljb25maWc6bWMxMjM0NTY="
        }
        res = requests.get(query_gc, headers=header, timeout=30)
        rlt = res.json()
        gcrlt = rlt["propertySources"][0]["source"]["gwzuul.companyIdToIzoneStr"]
        logger.info('【QueryInterface-query_grayCompany】查询灰度企业: %s, 入参: %s, 返回数据: %s', query_gc, header, gcrlt)
        return rlt

    def query_userInfo(self,userId,env):
        #根据userId查询用户信息
        HOSTS_URI = self.getUri(env)
        query_ui = HOSTS_URI + self.query_userinfo+userId
        req_json = ''
        res = requests.get(query_ui, data=req_json, timeout=30)
        logger.info('【QueryInterface-query_userInfo】根据userId查询用户信息: %s, 入参: %s, 返回数据: %s', query_ui, req_json, res.json())
        return res.json()

    def query_uidbyCP(self,companyId,phone,env):
        #根据phone和companyId查询用户信息
        HOSTS_URI = self.getUri(env)
        short_uri = "?companyId=%s&phone=%s"%(companyId,phone)
        query_ui = HOSTS_URI + self.query_userinfobycomphone+short_uri
        req_json = ''
        res = requests.get(query_ui, data=req_json, timeout=30)
        logger.info('【QueryInterface-query_uidbyCP】根据phone和companyId查询用户信息: %s, 入参: %s, 返回数据: %s', query_ui, req_json, res.json())
        return res.json()

    def query_pidbyCP(self,companyId,tel,env):
        #根据phone和companyId查询推荐官信息
        HOSTS_URI = self.getUri(env)
        short_uri = self.query_pidbycidat
        query_ui = HOSTS_URI + short_uri + '?companyId=%s&tel=%s'%(companyId,tel)
        req_json = ''
        res = requests.post(query_ui, data=req_json, timeout=30)
        logger.info('【QueryInterface-query_pidbyCP】根据phone和companyId查询推荐官信息: %s, 入参: %s, 返回数据: %s', query_ui, req_json, res.json())
        return res.json()


    def query_companyName(self,companyId,env):
        compInfo = self.query_companyInfo(companyId, env)
        if compInfo:
            try:
                companyName = compInfo['data']['companyName']
            except:
                companyName = '未知企业'
        else:
            companyName = "查询企业信息接口异常"
        return companyName