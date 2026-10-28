from. import requests,re, handle_request_errors
from.publicDef import publicDef

pdef = publicDef()

# 模块级 Session，复用 TCP 连接
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

class OVSetting(object):
    def __init__(self):
        self.querycompinfo_shorturl = "/user/unLogin/company/info"
        self.basicTestUri = "https://borigin-test.aijiatui.com" #基线版test
        self.basicPordUri = "https://borigin.aijiatui.com" #基线版prod
        self.soonTestUri = "https://soon-api-dev.aijiatui.com" #国际版test
        self.soonProdUri = "https://soon-api.aijiatui.com" #国际版prod
        self.meetTestUri = "https://meet-test.aijiatui.com" #中东版test-暂无
        self.meetProdUri = "https://meet-api.aijiatui.com" #中东版prod-已不可用
        self.twTestUri = "https://demon.aijiatui.com"  #通威版test
        self.twProdUri = "https://ai-card.aijiatui.com"  #通威版prod
        self.soon_token = ""
        self.basic_token = ""
        # 加密/解密接口的 admin token（按环境分开存储）
        self.soonAdminToken_test = ""   # test 环境 token
        self.soonAdminToken_prod = ""   # prod 环境 token
 
    def getphone(self,input_str):
        match = re.search(r'\+\d+-(\d+)', input_str)
        if match:
            print(pdef.logcss(gct(),"【ov_setting-getphone】"),"match phone:",match.group(1))
            return match.group(1)
        else:
            return None

    def versionUri(self,env,version,privaddr=""):
        mUri = ""
        print(f"versionUri: {version},{type(version)}")
        version = int(version)
        if env == "test":
            if version == 3: mUri = self.basicTestUri
            elif version == 4: mUri = self.soonTestUri
            # elif version == 5: mUri = self.meetTestUri
            elif version == 6: mUri = self.twTestUri
            elif version == 7: mUri = self.mmeettTestUri
        elif env == "prod":
            if version == 3:
                if privaddr: mUri = privaddr
                else: mUri = self.basicPordUri
            elif version == 4: mUri = self.soonProdUri
            # elif version == 5: mUri = self.meetProdUri
            elif version == 6: mUri = self.twProdUri
            elif version == 7: mUri = self.mmeettProdUri
        print(pdef.logcss(gct(),"【ov_setting-versionUri】"),"Uri by version:",mUri)
        return mUri
    #获取token
    @handle_request_errors()
    def gettoken(self,env,version):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/user/sms/login/mailLogin"
        req_json = {"mail":"cy@jt.com","password":"c4ca4238a0b923820dcc509a6f75849b","companyId":0}
        res = _get_session().post(uri, json = req_json)
        self.soon_token = res.json()['data']['token']
        print(pdef.logcss(gct(),"【ov_setting-gettoken】"),"soon_token:",self.soon_token)
        return res

    @handle_request_errors()
    def query_company_info(self,id,env,version):
        host_uri = self.versionUri(env,version)
        uri = host_uri + self.querycompinfo_shorturl
        req_json = {"id":id}
        res = _get_session().post(uri, json = req_json)
        print(pdef.logcss(gct(),"【ov_setting-query_company_info】"),"company info:",res.json())
        return res.json()

    @handle_request_errors()
    def getOprationAdminToken(self,env,version):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/admin/operate/login/account"
        req_json = {"password":"cf79ae6addba60ad018347359bd144d2","email":"admin@aijiatui.com"}
        res = _get_session().post(uri, json = req_json)
        print(pdef.logcss(gct(),"【ov_setting-query_company_info】"),"company info:",res.json())
        token = res.json()["data"][0]["token"]
        return token

    #基线版/soon企业开户
    @handle_request_errors()
    def origin_openAccount(self,cname,csname,phone,lname,pwd,langType,etime,env,version,privaddr=""):
        host_uri = self.versionUri(env,version,privaddr)
        uri = host_uri + "/user/unLogin/openAccount"
        if version == 4:
            token = self.getOprationAdminToken(env,version)
            req_json = {
                "companyName": cname,
                "shortName": csname,
                "phone": phone,
                "cardEmail": lname,
                "cardAddress": "",
                "cardHeadImage":"https://saas-static.aijiatui.com/base/defaultCardHeadImage.png",
                "languageType": langType,
                "expireTime": etime
            }
            vnm = "SOON"
        elif version == 3:
            token = ""
            req_json = {
                "companyName": cname,
                "shortName": csname,
                "phone": lname,
                "password": pwd,
                "languageType": langType,
                "expireTime": etime
            }
            vnm = "基线版"
        res = _get_session().post(uri, json=req_json, headers={"i-token": token})
        print(pdef.logcss(gct(),"【ov_setting-origin_openAccount】"),'【%s企业开户】:%s, 入参: %s, 返回数据: json:%s'%(vnm,uri,req_json,res.json()))
        return res.json()

    #设置soon名片版本
    @handle_request_errors()
    def soon_setVersion(self,compId,cardId,pversion,expTime,env,version=4):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/user/upgrade/setCompanyVersion"
        req_json = {
            "companyId": compId,
            "cardId": cardId,
            "version": pversion,
            "expireTime": expTime
        }
        res = _get_session().post(uri, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-soon_setVersion】"),'【设置soon名片版本】:%s, 入参: %s, 返回数据: json:%s'%(uri,req_json,res.json()))
        return res.json()

    #soon版员工名片绑定NFC卡片
    @handle_request_errors()
    def soon_setNfcService(self,cardId,code,env,version,lt = 1):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/user/nfc/device/set"
        req_json = {
            "cardId": cardId,
            "linkType": lt, #linkType: 1, 名片
            "code": code
        }
        res = _get_session().post(uri, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-soon_setNfcService】"),'【soon版员工名片绑定NFC卡片】:%s, 入参: %s, 返回数据: json:%s'%(uri,req_json,res.json()))
        return res.json()
    #soon版员工解绑NFC名片
    @handle_request_errors()
    def soon_rmvNfcService(self,code,env,version=4):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/user/nfc/device/remove"
        self.gettoken(env,version)
        header = {"i-token": self.soon_token}
        req_json = {"code":code}
        res = _get_session().post(uri, headers=header, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-soon_rmvNfcService】"),'【soon版员工解绑NFC卡片】:%s, 入参: %s, 返回数据: json:%s'%(uri,req_json,res.json()))
        return res.json()
    #获取shareId
    @handle_request_errors()
    def soon_getShareId(self,actionId,actionType,cardId,holderId,extensionJson,env,version):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/user/action/share"
        self.gettoken(env,version)
        header = {"i-token": self.soon_token}
        req_json = {"actionId":actionId,"actionType":actionType,"cardId":cardId,"holderId":holderId,"extensionJson":extensionJson}
        res = _get_session().post(uri, headers=header, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-soon_getShareId】"),'【soon版获取物料的shareID】:%s, 入参: %s, 返回数据: json:%s'%(uri,req_json,res.json()))
        return res.json()
    #获取extensionJson
    @handle_request_errors()
    def soon_getExtensionJson(self,actionId,actionType,cardId,holderId,env,version):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/user/share/config/get"
        self.gettoken(env,version)
        header = {"i-token": self.soon_token}
        req_json = {"actionId":actionId,"actionType":actionType,"cardId":cardId,"holderId":holderId}
        res = _get_session().post(uri, headers=header, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-soon_getExtensionJson】"),'【soon版获取物料的extensionJson】:%s, 入参: %s, 返回数据: json:%s'%(uri,req_json,res.json()))
        return res.json()
    #根据email查询userId
    @handle_request_errors()
    def soon_getUidByEmail(self,email,env,version):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/user/info"
        if "+" == email[:1] or "@" not in email:
            # if self.getphone(email).isdigit():
            keyname = "phone"
            if "1" == email[:1]:
                email = "+86-" + email
        else:
            keyname = "email"
        req_json = {keyname:email}
        res = _get_session().post(uri, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-soon_getUidByEmail】"),'【soon版根据email/phone查询userId】:%s, 入参: %s, 返回数据: json:%s'%(uri,req_json,res.json()))
        return res.json()
    #soon版根据userId查询userInfo
    @handle_request_errors()
    def soon_queryUserInfoByUid(self,uid,env,version):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/admin/user/detail"
        self.gettoken(env,version)
        header = {"i-token": self.soon_token}
        req_json = {"id":uid}
        res = _get_session().post(uri, headers=header, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-soon_queryUserInfoByUid】"),'【soon版根据userId查询userInfo】:%s, 入参: %s, 返回数据: json:%s'%(uri,req_json,res.json()))
        return res.json()
    #soon版设置用户新旧名片
    @handle_request_errors()
    def soon_setNewHome(self,userId,status,env,version):
        host_uri = self.versionUri(env,version)
        shortUri = "/user/setNewHome?userId=%s&status=%s"%(userId,status)
        uri = host_uri + shortUri
        req_json = ""
        res = _get_session().get(uri, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-soon_setNewHome】"),'【soon版设置用户新旧工作台】:%s, 入参: %s, 返回数据: json:%s'%(shortUri,req_json,res.json()))
        return res.json()
    #soon版手工发放时长
    @handle_request_errors()
    def soon_addduration(self,companyId,cardId,duration,dtype,etime,env,version):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/user/upgrade/duration/addDuration"
        self.gettoken(env,version)
        header = {"i-token": self.soon_token}
        req_json = {"companyId":companyId,"cardId":cardId,"duration":int(duration)*60,"durationType":dtype,"expireTime":etime}
        res = _get_session().post(uri, headers=header, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-soon_addduration】"),'【soon版手工发放时长】:%s, 入参: %s, 返回数据: json:%s'%(uri,req_json,res.json()))
        return res.json()
    #soon解绑翻译器
    @handle_request_errors()
    def soon_removeDevice(self,deviceNo,cardId,env,version):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/user/upgrade/bestow/remove"
        req_json = {"deviceNumber":deviceNo,"cardId":cardId}
        res = _get_session().post(uri, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-soon_removeDevice】"),'【soon版解绑翻译器】:%s, 入参: %s, 返回数据: json:%s'%(uri,req_json,res.json()))
        return res.json()
    #基线版企业绑定小程序(国际版暂无小程序)
    @handle_request_errors()
    def origin_saveOrUpdateWxAppInfo(self,cid,appid,secret,env,version=3,privaddr=""):
        host_uri = self.versionUri(env,version,privaddr)
        uri = host_uri + "/user/unLogin/saveOrUpdateWxAppInfo"
        req_json = {
            "companyId": cid,
            "appId": appid,
            "appSecret": secret
        }
        res = _get_session().post(uri, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-origin_saveOrUpdateWxAppInfo】"),'【基线版企业绑定小程序】:%s, 入参: %s, 返回数据: json:%s'%(uri,req_json,res.json()))
        return res.json()

    #基线版修改企业信息
    @handle_request_errors()
    def origin_updateCompanyInfo(self,cid,mta,cs,aics,isl,expt,env,version,privaddr=""):
        host_uri = self.versionUri(env,int(version),privaddr)
        uri = host_uri + "/user/unLogin/updateCompanyExpireTime"
        req_json = {
            "companyId": cid,
            "maxTotalAccount": mta,
            "companyStatus": cs
        }
        if isl:
            req_json["expireTime"] = expt
        if aics:
            req_json["aiCardSwitch"] = aics
        res = _get_session().post(uri, json=req_json)
        if int(version) == 3: cin = "基线版"
        elif int(version) == 4: cin = "Soon版"
        print(pdef.logcss(gct(),"【ov_setting-origin_updateCompanyInfo】"),'【%s修改企业信息】:%s, 入参: %s, 返回数据: json:%s'%(cin,uri,req_json,res.json()))
        return res.json()

    #基线版登录-获取token
    @handle_request_errors()
    def origin_loginaccount(self,phone,password,env,version=3):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/admin/login/account"
        req_json = {
            "phone": phone,
            "password": password
        }
        res = _get_session().post(uri, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-origin_loginaccount】"),'【基线版的登录获取token】:%s, 入参: %s, 返回数据: json:%s'%(uri,req_json,res.json()))
        # if res.json()['code'] == 0:
        #     token = res.json()['data'][0]['token']
        # else:
        #     token = res.json()['msg']
        return res.json()

    #修改用户密码
    @handle_request_errors()
    def origin_initpassword(self,userId,passwd,env,version=3):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/admin/init/user/password"
        if version == 3:
            gettoken = self.origin_loginaccount('17600000007','ce00580d6b3d1e0d7b7b8ec5eab0bc89',env)
            print('gettoken:',gettoken)
            self.basic_token = gettoken['data'][0]['token']
            lit = '基线版'
        # elif env == "proka":
        #     gettoken = self.proka_loginaccount("kristhe@aijiatui.com","c4ca4238a0b923820dcc509a6f75849b")
        #     itoken = gettoken['data']['token']
        #     lit = '国际版'
        headers = {
            "i-token":self.basic_token
        }
        req_json = {
            "userId": userId,
            "password": passwd
        }
        res = _get_session().post(uri,headers=headers, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-origin_initpassword】"),'【%s修改员工密码】:%s, 入参: %s, 返回数据: json:%s'%(lit,uri,req_json,res.json()))
        return res.json()
    #基线版-根据企业id查询企业信息
    @handle_request_errors()
    def getCompInfoByCompId(self,compId,env,version=3):
        host_uri = self.versionUri(env,version)
        uri = host_uri + self.querycompinfo_shorturl
        req_json = {
            "id": compId
        }
        res = _get_session().post(uri, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-getCompInfoByCompId】"),'【根据企业id查询企业信息】:%s, 入参: %s, 返回数据: json:%s'%(uri,req_json,res.json()))
        return res.json()

    #通威版企业开户
    @handle_request_errors()
    def tw_openAccount(self,cname,csname,adminName,lname,mta,etime,env,version=6,templateNo=""):
        host_uri = self.versionUri(env,version)
        print("origin_openAccount--host_uri:",host_uri)
        uri = host_uri + "/ai_card/admin/company/createCompany"
        req_json = {
            "companyName": cname,
            "shortName": csname,
            "adminName": adminName,
            "adminPhone": lname,
            "maxTotalAccount": mta,
            "expireTime": etime
        }
        if templateNo: req_json["templateNo"] = templateNo
        vnm = "通威版"
        res = _get_session().post(uri, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-tw_openAccount】"),'【%s企业开户】:%s, 入参: %s, 返回数据: json:%s'%(vnm,uri,req_json,res.json()))
        return res.json()
    
    #通威版企业绑定小程序
    @handle_request_errors()
    def tw_bindApplet(self,cid,appid,secret,env,version=6):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/ai_card/config/wxApp/saveConfig"
        req_json = {
            "companyId": cid,
            "appId": appid,
            "appSecret": secret
        }
        res = _get_session().post(uri, json=req_json)
        print(pdef.logcss(gct(),"【ov_setting-tw_bindApplet】"),'【通威版企业绑定小程序】:%s, 入参: %s, 返回数据: json:%s'%(uri,req_json,res.json()))
        return res.json()

    @handle_request_errors()
    def updateTWCompanyInfo(self,companyId,maxTotalAccount,expireTime,companyStatus,env,version=6):
        host_uri = self.versionUri(env,version)
        uri = host_uri + "/ai_card/admin/company/updateManageInfo"
        req_json = {
            "companyId": companyId,
            "maxTotalAccount": maxTotalAccount,
            "expireTime": expireTime,
            "companyStatus":companyStatus
        }
        res = _get_session().post(uri, json=req_json)
        print(f"updateTWCompanyInfo-res: {res}")
        print(pdef.logcss(gct(),"【ov_setting-updateTWCompanyInfo】"),'【通威版企业绑定小程序】:%s, 入参: %s, 返回数据: json:%s'%(uri,req_json,res.json()))
        return res.json()

    @handle_request_errors()
    def _loginAdmin(self, env, force_refresh=False):
        """Mmeett admin 登录（加密/解密接口需要）

        Args:
            env: 环境标识（test/prod）
            force_refresh: 是否强制刷新token（用于43265重试场景）
        """
        # 根据环境选择对应的 token 字段
        token_field = 'soonAdminToken_test' if env == 'test' else 'soonAdminToken_prod'
        cached_token = getattr(self, token_field, '')

        # 有缓存且不强制刷新，直接使用
        if cached_token and not force_refresh:
            print(pdef.logcss(gct(), "【ov_setting-_loginAdmin】"), f"环境: {env}; 使用缓存token")
            return {"code": 0, "msg": "使用缓存token", "data": [{"token": cached_token}]}

        # 重新登录获取token
        uri = self.soonTestUri if env == "test" else self.soonProdUri
        uri += '/admin/operate/login/account'
        data = {"password": "cf79ae6addba60ad018347359bd144d2", "email": "admin@aijiatui.com"}
        res = _get_session().post(uri, json=data)
        rlt = res.json()

        # 验证返回结构
        if not rlt.get("data") or not rlt["data"][0].get("token"):
            raise ValueError(f"登录接口返回结构异常: {rlt}")

        # 存储到对应的字段
        new_token = rlt["data"][0]["token"]
        setattr(self, token_field, new_token)
        print(pdef.logcss(gct(), "【ov_setting-_loginAdmin】"), f"环境: {env}; 获取新token成功 (force_refresh={force_refresh})")
        return rlt

    @handle_request_errors()
    def cryptoEncrypt(self, value, env, version):
        """加密（支持 token 自动刷新重试）"""
        verurl = self.versionUri(env, version)
        uri = verurl + "/admin/field-crypto/encrypt"

        # 首次请求（使用缓存token）
        self._loginAdmin(env)
        token_field = 'soonAdminToken_test' if env == 'test' else 'soonAdminToken_prod'
        header = {"i-token": getattr(self, token_field)}
        data = {"value": value}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()

        # 检测 token 失效（43265），自动强制刷新并重试
        if rlt.get("code") == 43265:
            print(pdef.logcss(gct(), "【ov_setting-cryptoEncrypt】"), f"Token 失效(43265)，强制刷新重试...")
            self._loginAdmin(env, force_refresh=True)  # 强制重新登录
            header = {"i-token": getattr(self, token_field)}
            res = _get_session().post(uri, headers=header, json=data)
            rlt = res.json()

        print(pdef.logcss(gct(), "【ov_setting-cryptoEncrypt】"), f"接口: {uri}; 入参:data={data}, header={header}; 返回: {rlt}")
        return rlt

    @handle_request_errors()
    def cryptoDecrypt(self, value, env, version):
        """解密（支持 token 自动刷新重试）"""
        verurl = self.versionUri(env, version)
        uri = verurl + "/admin/field-crypto/decrypt"

        # 首次请求（使用缓存token）
        self._loginAdmin(env)
        token_field = 'soonAdminToken_test' if env == 'test' else 'soonAdminToken_prod'
        header = {"i-token": getattr(self, token_field)}
        data = {"value": value}
        res = _get_session().post(uri, headers=header, json=data)
        rlt = res.json()

        # 检测 token 失效（43265），自动强制刷新并重试
        if rlt.get("code") == 43265:
            print(pdef.logcss(gct(), "【ov_setting-cryptoDecrypt】"), f"Token 失效(43265)，强制刷新重试...")
            self._loginAdmin(env, force_refresh=True)  # 强制重新登录
            header = {"i-token": getattr(self, token_field)}
            res = _get_session().post(uri, headers=header, json=data)
            rlt = res.json()

        print(pdef.logcss(gct(), "【ov_setting-cryptoDecrypt】"), f"接口: {uri}; 入参:data={data}; 返回: {rlt}")
        return rlt