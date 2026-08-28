from. import requests,logger
from.query_everything import queryEverything
from.publicDef import publicDef

qe = queryEverything()
pdef = publicDef()
HOSTS_URI_test = 'http://msr.jiatuitest.com'  # 测试
HOSTS_URI_prod = 'http://msr.jtscprod.com'  # 生产

def gct():
    return pdef.getctime()

class weComInterface(object):
    def __init__(self):
        self.appgoauthor = '/wxauth/agent/goAuthor2/' #应用授权的接口（直接返回授权链接，不重定向)
        self.getopencorpid = "/wxauth/wxapi/toOpenCorpId" #获取加密corpId
        self.delappletcfg = "/wxauth/openwx/applet/config/remove" #删除授权信息
    
    def appGoAuthor(self,companyId,appId,env):
        #生成企微应用授权链接
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        short_uri = self.appgoauthor + appId
        full_uri = HOSTS_URI+short_uri
        header = {
            "i-companyId":companyId
        }
        res = requests.get(full_uri, headers=header)
        print(pdef.logcss(gct(),'【forWeCom-weComInterface-appGoAuthor】'),'【生成企微应用授权链接】:%s, 入参: %s, 返回数据: %s'%(full_uri,header,res.json()))
        return res.json()

    def openCorpId(self,corpId,env):
        #根据明文的corpId获取加密corpId
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        short_uri = self.getopencorpid + "?corpId=%s"%corpId
        full_uri = HOSTS_URI+short_uri
        req_json = ""
        res = requests.post(full_uri, json=req_json)
        print(pdef.logcss(gct(),'【forWeCom-weComInterface-openCorpId】'),'【根据明文的corpId获取加密corpId】:%s, 入参: %s, 返回数据: %s'%(full_uri,req_json,res.json()))
        return res.json()
    def appletConfigRemove(self,companyId,appId,status,env):
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        short_uri = self.delappletcfg
        full_uri = HOSTS_URI+short_uri
        req_json = {
            "appId": appId,
            "companyIds": [companyId],
            "status":status
        }
        res = requests.post(full_uri, json=req_json)
        print(pdef.logcss(gct(),'【forWeCom-weComInterface-appletConfigRemove】'),'【删除公众号或小程序授权信息】:%s, 入参: %s, 返回数据: %s'%(full_uri,req_json,res.json()))
        return res.json()

class forWeCom(object):
    def __init__(self):
        self.wci = weComInterface()

    def getWeComAppAuthorLink(self,companyId,appId,env):
        aga = self.wci.appGoAuthor(companyId,appId,env)
        if aga['code'] == 0 and aga['msg'] == '成功':
            rlt = aga['data']
        else:
            rlt = aga['msg']
        return rlt

    def getOpenCorpId(self,corpId,env):
        oci = self.wci.openCorpId(corpId,env)
        if oci['code'] == 0 and oci['msg'] == '成功':
            if oci['data']['errcode'] == 0:
                rlt = "企微ID(密文): "+oci['data']['open_corpid']
            else:
                rlt = oci['data']['errmsg']
        else:
            rlt = '获取加密企微ID异常，',oci
        return rlt
    
    #删除授权信息
    def delAppletConfig(self,companyId,appId,status,env):
        acr = self.wci.appletConfigRemove(companyId,appId,status,env)
        if acr['code'] == 0 and acr['msg'] == '成功':
            if appId == 'card':
                rlt = '[%s]: 删除小程序绑定数据成功! '%companyId
            elif appId == 'wx_oa':
                rlt = '[%s]: 删除公众号绑定数据成功! '%companyId
            elif appId == 'cpe_backlog':
                rlt = '[%s]: 删除自建应用绑定数据成功! '%companyId
            elif appId == 'cpe_investment_applet':
                rlt = '[%s]: 删除招商小程序绑定数据成功! '%companyId
            elif appId == 'cpe_popularize_applet':
                rlt = '[%s]: 删除推广小程序绑定数据成功! '%companyId
            elif appId == 'cpe_partner_applet':
                rlt = '[%s]: 删除合伙人小程序绑定数据成功! '%companyId
            
        else:
            rlt = "接口调用失败，原因是: %s"%acr['msg']
        return rlt
