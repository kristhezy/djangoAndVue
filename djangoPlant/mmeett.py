from. import requests,handle_request_errors,Colors as s
from.publicDef import publicDef

pdef = publicDef()

# 模块级 Session，复用 TCP 连接避免重复 TLS 握手
_requests_session = None

def _get_session():
    global _requests_session
    if _requests_session is None:
        _requests_session = requests.Session()
        _requests_session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'djangoPlant/1.0',
        })
    return _requests_session

def gct(): #实时获取当前时间
    return pdef.getctime()

class mmeettIF(object):
    def __init__(self):
        self.mmeett_test = "https://vcard-api.aijiatui.com"
        self.mmeett_prod = "https://api.mmeett.com"
        self.token = ""
        self._token_env = ""       # 记录 token 对应的 env，env 变化时自动重新登录
        self.adminToken = ""
        self._adminToken_env = ""  # 同上
        self.email = ""
        self.vstId = ""

    def typeTransition(self,theName,theType):
        if type(theName) != theType: tn = theType(theName)
        else: tn = theName
        return tn
    
    def versionUri(self,env,version="7",vstver="0"):
        mUri = ""
        version = self.typeTransition(version,int)
        if vstver == "0":
            if env == "test": mUri = self.mmeett_test
            elif env == "prod": mUri = self.mmeett_prod
        return mUri
    
    @handle_request_errors()
    def mmeettResetPwd(self,email,code,pwd,repwd,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/user/resetPwd"
        req_json = {
            "email": email,
            "code": code,
            "newPassword": pwd,
            "passwordConfirm": repwd
        }
        res = _get_session().post(uri, json = req_json)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-mmeettResetPwd】"),f"接口: {uri}, 入参: {req_json}, 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def mmeettSendMailCode(self,email,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/user/notLoginSendMail/new"
        req_json = {
            "email": email,
            "kind": "2",
            "country": "",
            "lang": "",
            "thirdUid": ""
        }
        res = _get_session().post(uri, json = req_json)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-mmeettSendMailCode】"),f"接口: {uri}, 入参: {req_json}, 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def mmeettRegistNew(self,uname,pwd,repwd,country,rcode,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/user/register/new"
        header = {
            "language": "zh-Hans"
        }
        req_json = {
            "email": "", #该字段传值无用
            "userName": uname,
            "password": pwd,
            "passwordConfirm": repwd,
            "country": country,
            "referralCode": rcode,
            "deviceId": ""
        }
        res = _get_session().post(uri, headers=header, json = req_json)
        rlt = res.json()
        if rlt['code'] == 0:
            self.token = rlt['data']['jwtToken']['accessToken']
            self._token_env = env
        else:
            self.token = ""
            self._token_env = ""
        print(pdef.logcss(gct(),"【mmeettIF-mmeettRegistNew】"),f"接口: {uri}, 入参: {req_json}, 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def userlogin(self,username,env,version,password="qq123456"):
        # env 变了 → token 失效，重新登录
        if self._token_env and self._token_env != env:
            self.token = ""
        verurl = self.versionUri(env,version)
        uri = verurl + "/user/login"
        header = {
            "language": "zh-Hans"
        }
        req_json = {
            "loginType": "2",
            "email": "",
            "userName": username,
            "password": password
        }
        res = _get_session().post(uri, headers=header, json = req_json)
        rlt = res.json()
        if rlt['code'] == 0:
            self.token = rlt['data']['jwtToken']['accessToken']
            self._token_env = env
        else:
            self.token = ""
            self._token_env = ""
        print(pdef.logcss(gct(),"【mmeettIF-userlogin】"),f"接口: {uri}, 入参: {req_json}, 返回结果: {rlt}")
        return rlt

    @handle_request_errors()
    def queryUserInfo(self,email,env,version,remark=""):
        verurl = self.versionUri(env,version)
        uri = verurl + "/user/load"
        header = {
            "i-token": self.token,
            "language": "zh-Hans"
        }
        self.email = email
        res = _get_session().get(uri, headers=header)
        rlt = res.json()
        print(pdef.logcss(gct(),f"【mmeettIF-queryUserInfo {remark}】"),f"接口: {uri}, 入参:{header}, 返回结果: {rlt}")
        self.vstId = rlt['data']['user']['userId']
        return rlt

    @handle_request_errors()
    def sendEmail(self,env,version,kind,country=""): #发送邮箱验证码
        verurl = self.versionUri(env,version)
        uri = verurl + "/user/sendMail/new"
        header = {
            "i-token": self.token
        }
        data = {
	        "country": country,
            "email": self.email,
            "kind": kind
        }
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-sendEmail】"),f"接口: {uri}, 入参: {header},{data}, 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def bindAppEmail(self,env,version): #绑定邮箱
        verurl = self.versionUri(env,version)
        uri = verurl + "/user/bindAppEmail"
        header = {
            "i-token": self.token
        }
        data = {
            "id": self.vstId,
            "email": self.email,
            "code": "888888"
        }
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-bindAppEmail】"),f"接口: {uri}, 入参: {header},{data}, 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def updatePayPwd(self,env,version,pwd):
        verurl = self.versionUri(env,version)
        uri = verurl + "/user/updatePaymentPassword"
        header = {
            "i-token": self.token
        }
        data = {
            "email": self.email,
            "code": "888888",
            "password": pwd,
            "passwordConfirm": pwd
        }
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-updatePayPwd】"),f"接口: {uri}, 入参: {header},{data}, 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def rechargeConfig(self,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/user/vip/recharge/config/list"
        header = {
            "i-token": self.token,
            "language": "zh-Hans"
        }
        data = {}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-rechargeConfig】"),f"接口: {uri}, 入参: {header},{data}, 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def demotionVip(self,userId,level,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/admin/vip/demotionVip"
        if not self.adminToken: self.loginAdmin(env)
        header = {
            "i-token": self.adminToken
        }
        data = {"remark":"test by testplant","userId":userId,"validSeconds":0,"level":level}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-demotionVip】"),f"接口: {uri}; 入参:header={header},data={data}; 返回结果: {rlt}")
        return rlt

    @handle_request_errors()
    def purchase(self,id,psnum,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + f"/user/member/purchase/{id}"
        header = {
            "i-token": self.token,
            "language": "zh-Hans"
        }
        buytype = (30,1,3,35)
        data = {"id":f"{id}","deliveryWay":0,"takeGoodsCountry":"TW","activateCode":"","countryName":"臺灣","note":"","postcode":"123456","productSkus": psnum,"freight":0,"freightId":11,"takeGoodsName":"test","takeGoodsPhone":"+886","takeGoodsPhones":"123456","takeGoodsDetails":"test","activityId":"","activityGiveId":""}
        if int(id) in buytype: data["colors"] = [{"color":"grey","quantity":1}]
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-purchase】"),f"接口: {uri}, 入参: {header},{data}, 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def paymentOrder(self,poid,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + f"/user/payment/order/{poid}?id={poid}"
        header = {
            "i-token": self.token,
            "language": "zh-Hans"
        }
        res = _get_session().get(uri, headers=header)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-paymentOrder】"),f"接口: {uri}, 入参: {header}, 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def paymentRequest(self,poid,subject,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/user/payment/request"
        header = {
            "i-token": self.token,
            "language": "zh-Hans"
        }
        data = {
            "id": poid,
            "payCode": 0,
            "subject": subject,
            "password": "123123"
        }
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-paymentRequest】"),f"接口: {uri}; 入参: {header},{data}; 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def loginAdmin(self,env):
        # env 变了 → adminToken 失效，重新登录
        if self._adminToken_env and self._adminToken_env != env:
            self.adminToken = ""
        domain = self.versionUri(env)
        uri = domain + '/admin/login/account'
        if env == "test": psd = "6786d7956f9c7e55e6a5e1d12a89f3b0"
        if env == "prod": psd = "e29b3f14e80201979a4982a3149dcbc7"
        data = {"password":psd,"email":"meet@jiatui.com"}
        res = _get_session().post(uri,json = data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-loginAdmin】"),f"返回结果: {rlt}")
        self.adminToken = rlt["data"][0]["token"]
        self._adminToken_env = env
        return rlt

    @handle_request_errors()
    def openVip(self,userId,level,env):
        domain = self.versionUri(env)
        uri = domain + '/admin/vip/openVip'
        if not self.adminToken: self.loginAdmin(env)
        header = {"i-token": self.adminToken}
        data = {"remark":"test","level":level,"userId":userId,"validSeconds":2592000,"sendComputing":True,"sendAward":False}
        res = _get_session().post(uri,headers=header,json = data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【xcard-openVip】"),f"uri={uri}, header={header}, data={data}, response={rlt}")
        return rlt
    
    def rigestAndOpenVip(self,cs,uname,rcode,country,level,env,version):
        print(f"第「{cs+1}」次注册: ")
        pwd = "qq123456"
        repwd = pwd
        ru = self.mmeettRegistNew(uname,pwd,repwd,country,rcode,env,version)
        print(f"rigestAndOpenVip-regisetUser: {ru}")
        nrcode = ""
        rlt = ""
        if ru['code'] == 0 or ru['code'] == -27:
            if ru['code'] == 0: 
                rlt += f"用户{uname}注册成功！"
                self.userlogin(uname,env,version)
                qui = self.queryUserInfo(uname,env,version)
                if qui['code'] == 0:
                    userId = qui["data"]["user"]["jtUserId"]
                    nrcode = qui["data"]["user"]["referralCode"]
                    larlt = self.loginAdmin(env)
                    if larlt['code'] == 0:
                        ovrlt = self.openVip(userId, level, env)
                        if ovrlt['code'] == 0:
                            rlt += f"开通会员成功！<br/>"
                        else:
                            rlt += f"开通会员失败，原因：{ovrlt['msg']} <br/>"
                    else:
                        rlt += f"管理后台登录失败，原因：{larlt['msg']} <br/>"
                else:
                    rlt += f"查询用户信息失败，原因：{qui['msg']} <br/>"
            elif ru['code'] == -27: 
                rlt += f"用户{uname}已注册！<br/>"      
        else:
            rlt = f"用户{uname}注册失败，原因：{ru['msg']} <br/>"
        print(rlt)
        return nrcode,rlt
    
    @handle_request_errors()
    def getTree(self,env,version,userId="",deep=""):
        verurl = self.versionUri(env,version)
        uri = verurl + "/user/vip/hierarchy/getTree"
        header = {
            "i-token": self.token
        }
        print(f"getTree: userId={userId}, deep={deep}")
        if userId and deep == "": data = {"id":userId,"referralCode":""}
        elif deep: data={"id":userId,"deep":deep}
        else: data = {"deep":1}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-getTree】"),f"接口: {uri}; 入参:header={header},data={data}; ")
        return rlt

    @handle_request_errors()
    def getLocationInfo(self,userId,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/admin/vip/hierarchy/getNeedSetLocationInfoByUpdateUpperInfo"
        if not self.adminToken: self.loginAdmin(env)
        header = {
            "i-token": self.adminToken
        }
        data = {"referralCode":"","email":"","pageNum":1,"pageSize":10,"id":userId}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-getLocationInfo】"),f"接口: {uri}; 入参:header={header},data={data}; 返回结果: {rlt}")
        return rlt

    @handle_request_errors()
    def updateHierarchy(self,upperUserId,userId,side,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/admin/vip/hierarchy/update"
        if not self.adminToken: self.loginAdmin(env)
        header = {
            "i-token": self.adminToken
        }
        data = {"upperUserId":upperUserId,"lowerUserId":userId,"side":side,"remark":"test"}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-updateHierarchy】"),f"接口: {uri}; 入参:header={header},data={data}; 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def deleteUpperHierarchy(self,userId,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/admin/vip/hierarchy/deleteUpperHierarchy"
        if not self.adminToken: self.loginAdmin(env)
        header = {
            "i-token": self.adminToken
        }
        data = {"userId":userId,"remark":"切断上级树状关系"}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-deleteUpperHierarchy】"),f"接口: {uri}; 入参:header={header},data={data}; 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def deleteLowerHierarchy(self,userId,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/admin/vip/hierarchy/deleteLowerHierarchy"
        if not self.adminToken: self.loginAdmin(env)
        header = {
            "i-token": self.adminToken
        }
        data = {"userId":userId,"remark":"切断下级树状关系"}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-deleteLowerHierarchy】"),f"接口: {uri}; 入参:header={header},data={data}; 返回结果: {rlt}")
        return rlt

    @handle_request_errors()
    def updateUserInfo(self,userId,env,version,**kw):
        verurl = self.versionUri(env,version)
        uri = verurl + "/admin/user/update"
        if not self.adminToken: self.loginAdmin(env)
        header = {
            "i-token": self.adminToken
        }
        if "countryCode" in kw:
            data = {"id":userId,"countryCode":kw["countryCode"]}
            res = _get_session().post(uri, headers=header, json=data)
        if "account" in kw:
            data = {"id":userId,"account":kw["account"],"userName":kw["userName"]}
            res = _get_session().post(uri, headers=header, json=data)
        if "email" in kw:
            data = {"id":userId,"email":kw["email"]}
            res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-updateUserInfo】"),f"接口: {uri}; 入参:header={header},data={data}; 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def queryCountryInfo(self,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/user/country/all"
        header = {
            "language": "zh-Hans"
        }
        res = _get_session().get(uri,headers=header)
        rlt = res.json()
        print(pdef.logcss(gct(),"【mmeettIF-queryCountryInfo】"),f"接口: {uri}; 返回结果: {rlt}")
        return rlt

    @handle_request_errors()
    def dataRange(self,sd,ed,rtype,isPre,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/admin/vip/rerun/date-range"
        if isPre == 1: ipn = "预结算"
        if isPre == 0: ipn = "明细"
        header = {}
        data = {
            "startDateStr": sd,
            "endDateStr": ed,
            "type": rtype,
            "isPre": isPre
        }
        remark = f"dataRange-{ipn}"
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),f"【mmeettIF-{remark}】"),f"接口: {uri}; 入参:header={header},data={data}; 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def dataRangeSummary(self,sd,ed,rtype,env,version,rerunMode=""):
        verurl = self.versionUri(env,version)
        uri = verurl + "/admin/vip/rerun/date-range-summary"
        header = {}
        data = {
            "startDateStr": sd,
            "endDateStr": ed,
            "type": rtype
        }
        if int(rtype) == 43: data["rerunMode"] = rerunMode
        remark = "dataRangeSummary"
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),f"【mmeettIF-{remark}】"),f"接口: {uri}; 入参:header={header},data={data}; 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def getComputingRechargeConfigList(self,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/admin/vip/getComputingRechargeConfigList"
        if not self.adminToken: self.loginAdmin(env)
        header = {"i-token": self.adminToken}
        data = {}
        remark = "【getComputingRechargeConfigList】"
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),f"【mmeettIF-{remark}】"),f"接口: {uri}; 入参:header={header},data={data}; 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def sendComputing(self,id,userId,sa,crcl,env,version,ccnt=0):
        verurl = self.versionUri(env,version)
        uri = verurl + "/admin/vip/sendComputing"
        if int(id) > 0: rmk = next(i['name'] for i in crcl if int(i['id']) == int(id))
        else: rmk = "自定义"
        if int(sa) == 0: sendAward = False
        elif int(sa) == 1: sendAward = True
        data  = {"id":id,"sendAward":sendAward,"userId":userId,"remark": rmk}
        if int(id) == 0: data["computingCnt"] = ccnt
        if not self.adminToken: self.loginAdmin(env)
        header = {"i-token": self.adminToken}
        remark = f"sendComputing-{rmk}"
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),f"【mmeettIF-{remark}】"),f"接口: {uri}; 入参:header={header},data={data}; 返回结果: {rlt}")
        return rlt

    @handle_request_errors()
    def computingConsumption(self,userId,amount,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/admin/operate/computing/consumption"
        remark = "算力值扣减"
        data  = {"userId":userId,"remark": remark,"amount":amount}
        if not self.adminToken: self.loginAdmin(env)
        header = {"i-token": self.adminToken}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),f"【mmeettIF-{remark}】"),f"接口: {uri}; 入参:header={header},data={data}; 返回结果: {rlt}")
        return rlt

    @handle_request_errors()
    def sendAccountPoint(self,userId,level,amount,expire,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/admin/account/sendAccountPoint"
        if not self.adminToken: self.loginAdmin(env)
        header = {"i-token": self.adminToken}
        remark="赠送点位"
        data = {"remark":remark,"level":level,"userId":userId,"pointCount":amount,"vipExpireDays":expire}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),f"【mmeettIF-{remark}】"),f"接口: {uri}; 入参:header={header},data={data}; 返回结果: {rlt}")
        return rlt
    
    @handle_request_errors()
    def assetChange(self,userId,camount,state,env,version):
        verurl = self.versionUri(env,version)
        uri = verurl + "/admin/vip/asset/change"
        if not self.adminToken: self.loginAdmin(env)
        header = {"i-token": self.adminToken}
        states = {"0":"扣减","1":"充值"}
        remark="账户余额"+states.get(state,"")
        data = {"id":userId,"amount":camount,"remark":remark,"state":state}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(),f"【mmeettIF-{remark}】"),f"接口: {uri}; 入参:header={header},data={data}; 返回结果: {rlt}")
        return rlt

    @handle_request_errors()
    def getNeedSetInfo(self, userId, env, version):
        """查询待安置人数及列表"""
        verurl = self.versionUri(env, version)
        uri = verurl + "/admin/vip/hierarchy/getNeedSetInfo"
        if not self.adminToken: self.loginAdmin(env)
        header = {"i-token": self.adminToken}
        data = {"id": userId}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(), "【mmeettIF-getNeedSetInfo】"), f"接口: {uri}; 入参:data={data}; ")
        return rlt

    @handle_request_errors()
    def getNeedSetLocationInfo(self, userId, env, version):
        """查询可安置位置列表"""
        verurl = self.versionUri(env, version)
        uri = verurl + "/admin/vip/hierarchy/getNeedSetLocationInfo"
        if not self.adminToken: self.loginAdmin(env)
        header = {"i-token": self.adminToken}
        data = {"id": userId, "pageNum": 1, "pageSize": 1000}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(), "【mmeettIF-getNeedSetLocationInfo】"), f"接口: {uri}; 入参:data={data};")
        return rlt

    @handle_request_errors()
    def setHierarchy(self, upperUserId, lowerUserId, side, userId, env, version):
        """执行安置"""
        verurl = self.versionUri(env, version)
        uri = verurl + "/admin/vip/hierarchy/set"
        if not self.adminToken: self.loginAdmin(env)
        header = {"i-token": self.adminToken}
        data = {"upperUserId": upperUserId, "lowerUserId": lowerUserId, "side": side, "rootUserId": userId}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(), "【mmeettIF-setHierarchy】"), f"接口: {uri}; 入参:data={data}; 返回结果: {rlt}")
        return rlt

    @handle_request_errors()
    def delAccount(self, env, version=7):
        """用户注销 — POST /user/delAccount"""
        uri = (self.mmeett_test if env == 'test' else self.mmeett_prod) + '/user/delAccount'
        header = {'User-Agent': 'djangoPlant/1.0','i-token':self.token}
        data = {}
        print(pdef.logcss(gct(), '【mmeettIF-delAccount】'), f"接口: {uri}; 入参: {header}; ")
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()
        print(pdef.logcss(gct(), '【mmeettIF-delAccount】'), f"接口: {uri}; 入参: {data}; 返回: {rlt}")
        return rlt

