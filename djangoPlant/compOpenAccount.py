from. import requests
from.publicDef import publicDef

HOSTS_URI_test = 'http://msr.jiatuitest.com'  # 测试
HOSTS_URI_prod = 'http://msr.jtscprod.com'  # 生产
HOSTS_URI_nxlt = 'http://msr.qzds.nxunicom.local'  # 宁夏联通

pdef = publicDef()

def gct():
    return pdef.getctime()

class compOpenAccount(object):
    def __init__(self) -> None:
        self.saleskitsInit = "/company-center/center/company/popularizeInit"  #推广版初始化
        self.busk = "/crm-service/migrate/baseUpgradeSk" #销售工具版升级推广版
        self.coaccount = "/company-application-bff/bff/php-aggregation/agent/javaservice/account/open" #企业开户
        self.compscc = '/company-center/company-center/company/saveCustomizedCode' #新增/修改家装企业类型
    
    def getenv(self,env):
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        elif env == 'nxlt':
            HOSTS_URI = HOSTS_URI_nxlt
        return HOSTS_URI
        
    #加推saleskits版本初始化
    def jtSkInit(self,companyId,mta,mtpa,env,ctype):
        hosts = self.getenv(env)
        skinit = hosts + self.saleskitsInit
        req_json = {
            "companyId": companyId,
            "maxTotalAccount": mta,
            "maxTotalPartnerAccount": mtpa,
            "type":ctype
        }
        res = requests.post(skinit, json=req_json)
        if ctype == 1:
            typename = '家装'
        elif ctype == 0:
            typename = 'Saleskits'
        print(pdef.logcss(gct(),"【compOpenAccount-jtSkInit】"),f'【{typename}版配置】 \n接口地址: {skinit} \n入参: {req_json} \n返回数据: 头部:【{res.headers}】 \n内容:【{res.json()}】')
        return res.json()
    
    #销售工具版升级saleskits版接口
    def base_upgrade_sk(self,companyId,mta,mtpa,env):
        hosts = self.getenv(env)
        bsusk = hosts + self.busk + '?companyIds=%s&maxTotalAccount=%s&maxTotalPartnerAccount=%s'%(companyId,mta,mtpa)
        req_json = ''
        res = requests.get(bsusk, json=req_json)
        print(pdef.logcss(gct(),'【compOpenAccount-base_upgrade_sk】'),f'【销售工具版升级saleskits版】 \n接口地址: {bsusk} \n入参: {req_json} \n返回数据: 头部:【{res.headers}】 \n内容:【{res.json()}】' )
        return res.json()

    #企业开户
    def comp_openAccount(self,cname,ctype,etime,lname,pwd,env):
        hosts = self.getenv(env)
        compoa = hosts + self.coaccount
        req_json = {
            "companyName": cname,
            "companyType": ctype,
            "expireTime": etime,
            "loginName": lname,
            "maxRadarNum": 0,
            "maxStoreNum": 0,
            "maxTotalAccount": 0,
            "password": pwd
            }
        res = requests.post(compoa, json=req_json)
        print(pdef.logcss(gct(),'【compOpenAccount-comp_openAccount】'),f'【企业开户】 \n接口地址: {compoa} \n入参: {req_json} \n返回数据: 头部:【{res.headers}】 \n内容:【{res.json()}】')
        return res.json()

    #新增/修改家装企业类型
    def saveCustomizedCode(self,cid,code,remark,env):
        hosts = self.getenv(env)
        scc = hosts + self.compscc
        req_json = {
            "companyId": cid,
            "code": code,
            "remark": remark
            }
        res = requests.post(scc, json=req_json)
        print(pdef.logcss(gct(),'【compOpenAccount-saveCustomizedCode】'),'【新增/修改家装企业类型】 \n接口地址: {scc} \n入参: {req_json} \n返回数据: 头部:【{res.headers}】 \n内容:【{res.json()}】')
        return res.json()

