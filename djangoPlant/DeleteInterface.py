from. import requests,logger
from.publicDef import publicDef

HOSTS_URI_test = 'http://msr.jiatuitest.com'  # 测试
HOSTS_URI_prod = 'http://msr.jtscprod.com'  # 生产
HOSTS_URI_ydtest = 'http://test.msr.jt.adenfin.com'  # 亚丁投资顾问平台-测试环境
HOSTS_URI_hmzx = 'http://test.msr.jt.changfeng666.com' #亚丁线索顾问平台
pdef = publicDef()

def gct():
    return pdef.getctime()

class DeleteInterface():
    def __init__(self):
        self.delCuleUser = "/referral/delCuleUser"  #删除企业访客/线索信息 3
        self.cleanPartnerAppletInfo = "/loginservice/card/investment/applet/cleanPartnerAppletInfo" #删除合伙人信息和合伙人登录token
        self.cleanPartnerAppletToken = "/loginservice/card/investment/applet/cleanPartnerAppletToken"  #清除合伙人小程序的登录token 1
        self.deletePartner = "/ai-retail-store/retail/partner/deletePartner" #删除合伙人小程序创建合伙人专用 2
        # self.ydDeletePartner = '/ai-retail-store/retail/partner/deletePartner'  #亚丁删除顾问专用

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
        return HOSTS_URI

    def del_clueUser(self,companyId,userId,env):
        #删除企业访客/线索信息（测试专用）
        if env == 'prod':
            if str(companyId) in (''):
                HOSTS_URI = HOSTS_URI_prod+'/hip/crm-service/10.100.0.137/80'
            else:
                HOSTS_URI = HOSTS_URI_prod+'/crm-service'
        else:
            HOSTS_URI = self.getUri(env) + '/crm-service'
        query_rui = HOSTS_URI+self.delCuleUser
        print('del_clueUser:',query_rui)
        header = {
            "i-companyId": companyId,
            "Content-Type": "application/json"
        }
        req_json = [userId]
        res = requests.post(query_rui,headers= header, json=req_json)
        print(pdef.logcss(gct(),'【DeleteInterface-del_clueUser】'),f'【删除企业访客/线索信息】:{query_rui}, 入参:【header:{header},body:{req_json}】, 返回数据: 【header:{res.headers};data:{res.json()}】')
        return res.json()
    
    def clean_partnerAppletInfo(self, companyId, userId, distributorId, env):
        #删除合伙人信息和合伙人登录token
        HOSTS_URI = self.getUri(env)
        short_uri = self.cleanPartnerAppletInfo
        all_uri = HOSTS_URI+short_uri
        req_json={
            "companyId":companyId,
            "userId": userId,
            "distributorId":distributorId
        }
        res = requests.post(all_uri,json=req_json)
        print(pdef.logcss(gct(),'【DeleteInterface-del_clueUser】'),f'【清除合伙人小程序的登录token】:{all_uri}, 入参:{req_json}, 返回数据: {res.json()}')
        return res.json()
    
    def del_partnerInfo(self,companyId,userId,partnerId,env):
        #删除合伙人小程序创建合伙人专用
        HOSTS_URI = self.getUri(env)
        query_rui = HOSTS_URI+self.deletePartner
        req_json = {
            "companyId": companyId,
            "partnerId": partnerId,
            "userId": userId
        }
        res = requests.post(query_rui, json=req_json)
        print(pdef.logcss(gct(),'【DeleteInterface-del_clueUser】'),f'【删除合伙人信息】:{query_rui}, 入参: {req_json}, 返回数据: {res.json()}')
        return res.json()

