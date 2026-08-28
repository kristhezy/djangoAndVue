from. import requests,datetime
from.publicDef import publicDef

pdef = publicDef()
# HOSTS_URI = 'http://msr.jtscprod.com'  # 生产
HOSTS_URI_test = 'http://msr.jiatuitest.com'  # 测试
HOSTS_URI_prod = 'http://msr.jtscprod.com'  # 生产
t = 'test'
jcc = 'jt_company_center'

def gct(): #实时获取当前时间
    c_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return str(c_time)

class dzFunction():
    def __init__(self):
        self.hmycuststatus = "/crm-service/hmy/dataSync/syncCustomerStatus"
        self.hmygetcustbycfid = "/crm-service/homedecoration/custForm/getDetailById?id="
        self.getfollowstatus="/crm-service/follow/status/list"
        self.hwylicenseactivate = "/company-center/company-center/license/activate"
    
    def gethost(self,env):
        HOST_URI = ""
        if env == 'test':
            HOST_URI = HOSTS_URI_test
        elif env == "prod":
            HOST_URI = HOSTS_URI_prod
        return HOST_URI

    #红蚂蚁企业更新客户阶段
    def hmy_updateFollowStatus(self, cfid, fs, env):
        print("dzFunction--hmy_updateFollowStatus-env:",env)
        HOSTS_URI = self.gethost(env)
        if HOSTS_URI:
            uri = HOSTS_URI+self.hmycuststatus
            req_json = {
                "customerId":cfid,
                "status":fs
            }# customerId = customerFormId, tatus: 0、1、2... 等于生命周期中的节点，第一个是0，以此类推
            res = requests.post(uri, json=req_json)
            print(gct(),'【红蚂蚁企业更新客户阶段】:%s, 入参: %s, 返回数据: %s' %(uri,req_json,res.json()))
            rlt = res.json()
        else:
            rlt = "获取域名失败，%s" %HOSTS_URI
        return rlt
    def hmy_queryCustDetailByCFID(self, id, env):
        print("dzFunction--hmy_queryCustDetailByCFID-env:",env)
        HOSTS_URI = self.gethost(env)
        if HOSTS_URI:
            uri = HOSTS_URI+self.hmygetcustbycfid+id
            req_json = ""
            res = requests.get(uri, json=req_json)
            print(gct(),'【根据customerformId查询客户信息】:%s, 入参: %s, 返回数据: %s' %(uri,req_json,res.json()))
            rlt = res.json()
        else:
            rlt = "获取域名失败，%s" %HOSTS_URI
        return rlt
    def queryFollowStatus(self,companyId,env):
        print("dzFunction--queryFollowStatus-env:",env)
        HOSTS_URI = self.gethost(env)
        if HOSTS_URI:
            uri = HOSTS_URI+self.getfollowstatus
            req_json = {"companyId":companyId}
            res = requests.post(uri, json=req_json)
            print(gct(),'【根据customerformId查询客户信息】:%s, 入参: %s, 返回数据: %s' %(uri,req_json,res.json()))
            rlt = res.json()
        else:
            rlt = "获取域名失败，%s" %HOSTS_URI
        return rlt

    def hwy_registLisence(self,compId,lisence,env):
        HOSTS_URI = self.gethost(env)
        if HOSTS_URI:
            uri = HOSTS_URI+self.hwylicenseactivate
            req_json = {"companyId":compId,"license":lisence}
            res = requests.post(uri, json=req_json)
            print(gct(),'【华为云私有化lisence激活】:%s, 入参: %s, 返回数据: %s' %(uri,req_json,res.json()))
            rlt = res.json()
        else:
            rlt = "华为云私有化lisence激活失败，%s" %HOSTS_URI
        return rlt