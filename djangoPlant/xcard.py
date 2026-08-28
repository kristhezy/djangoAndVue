from. import requests,handle_request_errors
from.publicDef import publicDef

pdef = publicDef()

def gct(): #实时获取当前时间
    return pdef.getctime()


class xcard(object):
    def __init__(self):
        self.testenv = "https://xcard-api.aijiatui.com"
        self.idprodenv = "https://api.xcard-pay.com"
        self.thtestenv = "https://xcard-th-api-dev.aijiatui.com"
        self.thprodenv = "https://api.x-luxe.cc"
        self.nlsendmail = "/user/notLoginSendMail/new"
        self.registnew = "/user/register/new"
        self.userlogin = "/user/login"
        self.sendmail = "/user/sendMail/new"
        self.setpaymentpwd = "/user/updatePaymentPassword"
        self.purchase = "/user/member/purchase/"
        self.getorder = "/user/payment/order/"
        self.payment = "/user/payment/request"
        self.country = "/user/country/all"
        self.twOrderPreview = "/user/mall/order/create/preview"
        self.twOrderCreate = "/user/mall/order/create"
        self.twPaymentRquest = "/user/payment/request"
        self.twAddAddress = "/user/mall/address/add"
        self.token = ""
        self.adminToken = ""
        self.ct = ""

    def getDomain(self,desc,env):
        if env == "test":
            if desc == "indo": domain = self.testenv
            elif desc == "taiwan": domain = self.thtestenv
        elif env == "prod":
            if desc == "indo": domain = self.idprodenv
            elif desc == "thai": domain = self.thprodenv
        else: domain = ""
        return domain
    
    @handle_request_errors()
    def getCountry(self,desc,env):
        resName = "【xcard-getCountry】"
        domain = self.getDomain(desc,env)
        uri = domain + self.country
        header = {"language":"zh-Hans"}
        res = requests.get(uri,headers=header)
        rlt = res.json()
        print(pdef.logcss(gct(),resName),f"接口: {uri},返回结果: {rlt}")
        return rlt

    @handle_request_errors()
    def rigestSendMail(self,email,desc,env):
        domain = self.getDomain(desc,env)
        print(f"regisetSendMail-domain: {domain}")
        uri = domain + self.nlsendmail
        data = {
            "email": email,
            "kind": 1
        }
        res = requests.post(uri, json=data)
        print(f"regisetSendMail res: {uri}, data: {data}, res: {res}")
        rlt = res.json()
        return rlt

    @handle_request_errors()
    def registUser(self,email,rcode,country,desc,env):
        domain = self.getDomain(desc,env)
        uri = domain + self.registnew
        data = {
            "account": "",
            "email": email,
            "code": "202601",
            "password": "45101b093c4e8acf32a525dc231afd50",
            "country": country,
            "referralCode": rcode,
        }
        res = requests.post(uri, json=data)
        print(f"registUser ==> uri:{uri}, data:{data}, resrlt:{res.json()}")
        rlt = res.json()
        return rlt

    @handle_request_errors()
    def getTokenByLogin(self,email,desc,env):
        domain = self.getDomain(desc,env)
        uri = domain + self.userlogin
        data = {"email":email,"password":"45101b093c4e8acf32a525dc231afd50","loginType":1}
        res = requests.post(uri, json=data)
        rlt = res.json()
        self.token = rlt["data"]["jwtToken"]["accessToken"]
        return rlt

    @handle_request_errors()
    def queryUserInfo(self,email,desc,env):
        domain = self.getDomain(desc,env)
        uri = f"{domain}/user/load"
        header = {"i-token":self.token}
        res = requests.get(uri, headers=header)
        rlt = res.json()
        return rlt

    @handle_request_errors()
    def sendMail(self,email,desc,env):
        domain = self.getDomain(desc,env)
        uri = domain + self.sendmail
        header = {"i-token":self.token}
        data = {"email":email,"kind":8}
        res = requests.post(uri, headers=header, json=data)
        rlt = res.json()
        return rlt

    @handle_request_errors()
    def setPaymentPassword(self,email,desc,env):
        domain = self.getDomain(desc,env)
        uri = domain + self.setpaymentpwd
        header = {"i-token":self.token}
        data = {"email":email,"code":"202601","password":"4297f44b13955235245b2497399d7a93","passwordConfirm":"4297f44b13955235245b2497399d7a93"}
        res = requests.post(uri, headers=header, json=data)
        rlt = res.json()
        return rlt

    @handle_request_errors()
    def memberPurchase(self,email,cardType,desc,env):
        self.ct = cardType
        domain = self.getDomain(desc,env)
        uri = domain + self.purchase + cardType
        header = {"i-token":self.token}
        data = {"vipId":cardType,"deliveryWay":0,"takeGoodsCountry":"ID","countryName":"印尼","takeGoodsName":"1","takeGoodsPhone":"+62","takeGoodsPhones":"1","takeGoodsDetails":"1","note":"","postcode":"1","freight":1000,"freightId":42}
        res = requests.post(uri, headers=header, json=data)
        rlt = res.json()
        return rlt

    @handle_request_errors()
    def paymentOrder(self,email,orderId,desc,env):
        domain = self.getDomain(desc,env)
        uri = domain + self.getorder + f"{orderId}?id={orderId}"
        header = {"i-token":self.token}
        res = requests.get(uri, headers=header)
        rlt = res.json()
        print(f"paymentOrder: uri={uri}, header={header}, res={rlt}")
        return rlt

    @handle_request_errors()
    def paymentRequest(self,email,orderId,desc,env,productName=""):
        domain = self.getDomain(desc,env)
        uri = domain + self.payment
        header = {"i-token":self.token}
        if self.ct == "1": ctn = "银卡销售"
        elif self.ct == "2": ctn = "金卡销售"
        elif self.ct == "3": ctn = "黑卡销售"
        else: ctn = productName
        data = {"id":orderId,"payCode":0,"subject":ctn,"password":"4297f44b13955235245b2497399d7a93"}
        res = requests.post(uri, headers=header, json=data)
        rlt = res.json()
        print(f"faymentRequest: uri={uri}, header={header}, data={data}, res={rlt}")
        return rlt

    @handle_request_errors()
    def addAddressId(self,countryCode,countryName,areaCode,desc,env):
        resName = "【xcard-addAddressId]"
        domain = self.getDomain(desc,env)
        uri = domain + self.twAddAddress
        header = {"i-token":self.token}
        data = {"addressId":"","countryCode":countryCode,"countryName":countryName,"consigneeMobile":f"+{areaCode}-88888888","consigneeName":"test","address":"test","postalCode":"888888","isDefault":1}
        res = requests.post(uri, json=data, headers=header)
        rlt = res.json()
        print(pdef.logcss(gct(),resName),f"接口: {uri},返回结果: {rlt}")
        return rlt

    @handle_request_errors()
    def orderPreview(self,productId,addressId,desc,env):
        resName = "【xcard-orderPreview】"
        domain = self.getDomain(desc,env)
        uri = domain + self.twOrderPreview
        header = {"i-token":self.token}
        data = {"productList":[{"productId":productId,"quantity":1}],"addressId":addressId}
        res = requests.post(uri, json=data, headers=header)
        rlt = res.json()
        print(pdef.logcss(gct(),resName),f"接口: {uri},返回结果: {rlt}")
        return rlt

    @handle_request_errors()
    def orderCreate(self,productId,addressId,desc,env):
        resName = "【xcard-orderCreate】"
        domain = self.getDomain(desc,env)
        uri = domain + self.twOrderCreate
        header = {"i-token":self.token}
        data = {"productList":[{"productId":productId,"quantity":1}],"addressId":addressId}
        res = requests.post(uri, json=data, headers=header)
        rlt = res.json()
        print(pdef.logcss(gct(),resName),f"接口: {uri},入参:{data}, 返回结果: {rlt}")
        return rlt

    @handle_request_errors()
    def loginAdmin(self,desc,env):
        domain = self.getDomain(desc,env)
        uri = domain + '/admin/login/account'
        data = {"password":"6786d7956f9c7e55e6a5e1d12a89f3b0","email":"xcard@jiatui.com"}
        res = requests.post(uri,json = data)
        rlt = res.json()
        print(f"xcard-loginAdmin: {rlt}")
        self.adminToken = rlt["data"][0]["token"]
        return rlt

    @handle_request_errors()
    def openVip(self,userId,cardType,desc,env):
        domain = self.getDomain(desc,env)
        uri = domain + '/admin/vip/openVip'
        header = {"i-token": self.adminToken}
        data = {"remark":"1","level":cardType,"userId":userId,"sendAward":False}
        res = requests.post(uri,headers=header,json = data)
        rlt = res.json()
        print(f"xcard-openVip: {rlt}")
        return rlt
    
    def rigestAndOpenVip(self,cs,email,rcode,country,cardType,desc,env):
        print(f"第「{cs+1}」次注册: ")
        self.rigestSendMail(email,desc,env)
        ru = self.registUser(email,rcode,country,desc,env)
        print(f"rigestAndOpenVip-regisetUser: {ru}")
        nrcode = ""
        rlt = ""
        if ru['code'] == 0 or ru['code'] == -27:
            if ru['code'] == 0: rlt += f"用户{email}注册成功！"
            elif ru['code'] == -27: rlt += f"用户{email}已注册！"
            self.getTokenByLogin(email,desc,env)
            qui = self.queryUserInfo(email,desc,env)
            if qui['code'] == 0:
                userId = qui["data"]["userVipInfo"]["userId"]
                nrcode = qui["data"]["userVipInfo"]["referralCode"]
                larlt = self.loginAdmin(desc,env)
                if larlt['code'] == 0:
                    ovrlt = self.openVip(userId, cardType, desc, env)
                    if ovrlt['code'] == 0:
                        rlt += f"开通会员成功！<br/>"
                    else:
                        rlt += f"开通会员失败，原因：{ovrlt['msg']} <br/>"
                else:
                    rlt += f"管理后台登录失败，原因：{larlt['msg']} <br/>"
            else:
                rlt += f"查询用户信息失败，原因：{qui['msg']} <br/>"
        else:
            rlt = f"用户{email}注册失败，原因：{ru['msg']} <br/>"
        print(rlt)
        return nrcode,rlt