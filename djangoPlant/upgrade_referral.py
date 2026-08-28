"""
升级转介绍3.0时，需要做如下操作：
    1、修改企业类型；
    2、修改企业的打款方式；
    3、增加企业的'M127'&'M128'模块；
    4、增加企业的总席位数；
    5、数据迁移。
"""

from. import requests
from.publicDef import publicDef

pdef = publicDef()
def gct():
    return pdef.getctime()

class UpgradeReferral():

    def __init__(self):  
        self.HOSTS_URI_test = 'http://msr.jiatuitest.com'  # 测试
        self.HOSTS_URI_prod = 'http://msr.jtscprod.com'  # 生产
        self.company_type = 7
        self.payment = 3
    #获取接口域名
    def getUri(self,env):
        HOSTS_URI=""
        if env == 'prod':
            HOSTS_URI = self.HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = self.HOSTS_URI_test
        return HOSTS_URI
    #更新企业信息
    def update_companyInfo(self, company_id, env, **kw):
        HOSTS_URI = self.getUri(env)
        short_uri = '/company-center/center/company/update'
        updata_company_info = HOSTS_URI + short_uri
        # 1. 定义参数名到接口字段名的映射
        FIELD_MAP = {
            'company_type': 'companyType',
            'seat_account': 'maxTotalAccount',
            'partner_seat_account': 'maxTotalPartnerAccount',
            'radar_num': 'maxRadarNum',
            'company_status': 'companyStatus',
            'company_name': 'companyName',
            'admin_name': 'adminName',
        }
        # 2. 使用字典解包（**）合并固定字段与动态匹配字段
        req_json = {
            "companyId": company_id,
            **{
                FIELD_MAP[k]: v 
                for k, v in kw.items() 
                if k in FIELD_MAP
            }
        }
        res = requests.post(updata_company_info, json=req_json)
        try:
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(pdef.logcss(gct(),'【upgrade_referral-update_companyInfo】'),'【修改企业信息】:%s, 入参: %s, 返回数据: json:%s'%(short_uri,req_json,rlt))
        return rlt

    #延迟修改企业席位
    def delay_updateTotalSeat(self, company_id, totalAccountNum, env, updateTime):
        HOSTS_URI = self.getUri(env)
        short_uri = '/company-center/company-center/pay/company/account/update/delay' #延迟更新企业总账号
        delay_update_totalSeat = HOSTS_URI + short_uri
        req_json = {
            "companyId":company_id,
            "totalAccountNum": totalAccountNum,
            "updateTime": updateTime
        }
        res = requests.post(delay_update_totalSeat, json=req_json)
        print(pdef.logcss(gct(),'【upgrade_referral-delay_updateTotalSeat】'),'【延迟修改企业总席位】:%s, 入参: %s, 返回数据: %s' %(short_uri,req_json,res.json()))
        return res.json()

    #修改企业有效期（同步至代理商后台）
    def update_company_expireTime(self, company_id, expire_time, env):
        #修改企业有效期（同步至代理商后台）
        HOSTS_URI = self.getUri(env)
        short_uri = '/company-center/company-center/company/modified_expired_time'
        updata_company_info = HOSTS_URI + short_uri + '?companyId=%s&expireTime=%s' %(company_id, expire_time)
        req_json = ''
        res = requests.post(updata_company_info, json=req_json)
        # print('【修改企业打款方式】: ',res.json())
        print(pdef.logcss(gct(),'【upgrade_referral-update_company_expireTime】'),'【修改企业有效期】:%s, 入参: %s, 返回数据: %s' %(short_uri,req_json,res.json()))
        return res.json()

    #修改企业打款方式（1，线下；3，预充值）
    def update_company_payment(self, company_id, payment, env):
        # 修改企业打款方式
        HOSTS_URI = self.getUri(env)
        short_uri = '/company-center/company-center/company/payment/set'
        updata_payment = HOSTS_URI + short_uri
        req_json = {
            "payment": payment,
            "companyId": company_id
        }
        try:
            res = requests.post(updata_payment, json=req_json)
            rlt = res.json()
        except Exception as e:
            rlt = e
        # print('【修改企业打款方式】: ',res.json())
        print(pdef.logcss(gct(),'【upgrade_referral-update_company_payment】'),'【修改企业打款方式】:%s, 入参: %s, 返回数据: %s' %(short_uri,req_json,rlt))
        return rlt

    #修改企业的第三方人力资源（默认值为1）
    def update_company_thirdparty(self, company_id, thirdparty_id, env):
        # 增加企业的总席位数
        HOSTS_URI = self.getUri(env)
        short_uri = '/company-center/company-center/contract/setCompanyThirdParty?companyId=%s&thirdPartyId=%s' %(company_id, thirdparty_id)
        updata_company_tp = HOSTS_URI + short_uri
        req_json = ''
        # print('【修改企业的第三方人力资源】: ',res.json())
        try:
            res = requests.get(updata_company_tp)
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(pdef.logcss(gct(),'【upgrade_referral-update_company_thirdparty】'),'【修改企业的第三方人力资源】:%s, 入参: %s, 返回数据: %s' %(updata_company_tp,req_json,rlt))
        return rlt
    #修改员工雷达状态
    def updata_radar_status(self, company_id, cardIds, radar_status, company_type, env):
        # 修改员工雷达状态
        HOSTS_URI = self.getUri(env)
        short_uri = '/company-center/company-center/radar/modify/status' #批量修改雷达状态
        updata_company_tp = HOSTS_URI + short_uri
        headers = {
            "content-type": "application/json;charset=UTF-8",
            "i-companyId": company_id
        }
        req_json = {
            "cardIds": cardIds,
            "companyType": company_type,
            "radarStatus": radar_status
        }
        try:
            res = requests.post(updata_company_tp, headers=headers, json=req_json)
            rlt = res.json()
        except Exception as e:
            rlt = e
        # print('【修改企业的第三方人力资源】: ',res.json())
        print(pdef.logcss(gct(),'【upgrade_referral-updata_radar_status】'),'【批量修改雷达状态】:%s, 入参: %s, 返回数据: %s' %(short_uri,req_json,rlt))
        return rlt

    #保存优惠券2.0配置
    def save_coupon_config(self, company_id, env):
        HOSTS_URI = self.getUri(env)
        short_uri = '/oa-service/oa-service/common/system/config/saveOrUpdate'
        add_module = f"{HOSTS_URI}"+short_uri
        req_json = {
            "key": company_id, 
            "serviceLineEnum": "OS", 
            "type": "COUPON_TYPE", 
            "value": "1"
        }
        try:
            res = requests.post(add_module, json=req_json)
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(pdef.logcss(gct(),'【upgrade_referral-save_coupon_config】'),'【保存优惠券2.0配置】:%s, 入参: %s, 返回数据: %s' %(short_uri,str(req_json),str(rlt)))
        return rlt

    #添加/开启企业模块
    def add_company_module(self, company_id, module_key, env):
        # 增加企业模块
        HOSTS_URI = self.getUri(env)
        short_uri = '/company-center/company-center/company/module/add'
        add_module = f"{HOSTS_URI}"+short_uri
        req_json = {
            "moduleKey": module_key,
            "companyId": company_id
        }
        res = requests.post(add_module, json=req_json)
        if res.status_code == 200:
            print(pdef.logcss(gct(),'【upgrade_referral-add_company_module】'),'【增加企业模块】:%s, 入参: %s, 返回数据: %s' %(short_uri,req_json,res.json()))
            return res.json()
        else:
            print(pdef.logcss(gct(),'【upgrade_referral-add_company_module】','error'),"添加/开启企业模块接口异常，",res)
            return {"code":77001,"msg":"添加/开启企业模块接口异常"}

    #关闭企业模块
    def del_company_module(self, company_id, module_key, env):
        # 删除企业模块
        HOSTS_URI = self.getUri(env)
        short_uri = '/company-center/company-center/company/module/delete'
        del_module = f"{HOSTS_URI}"+short_uri
        req_json = {
            "moduleKey": module_key,
            "companyId": company_id
        }
        res = requests.post(del_module, json=req_json)
        if res.status_code == 200:
            print(pdef.logcss(gct(),'【upgrade_referral-del_company_module】'),'【删除企业模块】:%s, 入参: %s, 返回数据: %s' %(short_uri,req_json,res.json()))
            return res.json()
        else:
            print(pdef.logcss(gct(),'【upgrade_referral-del_company_module】','error'),"关闭企业模块接口异常，",res)
            return {"code":77002,"msg":"关闭企业模块接口异常"}

    #数据迁移-基础版升级转介绍3.0
    def migrate_data(self, company_id, env):
        HOSTS_URI = self.getUri(env)
        req_json = {
            "companyIds": company_id
        }
        short_uri = '/crm-service/migrate/migrateData3?companyIds=%s' %company_id
        migrate_data_url = f"{HOSTS_URI}"+short_uri
        res = requests.get(migrate_data_url, json=req_json)
        re = res.json()
        # print('【基础版数据迁移日志】: ',re)
        print(pdef.logcss(gct(),'【upgrade_referral-migrate_data】'),'【基础版数据迁移日志】:%s, 入参: %s, 返回数据: %s' %(short_uri,req_json,re))
        if res.status_code == 200 :
            # print(res.headers['x-envoy-upstream-service-time'], )
            if re['code'] == 0 and re['msg'] == '成功':
                return ">>>升级3.0数据完成，用时 % s 毫秒。" % res.headers['x-envoy-upstream-service-time']
        elif res.status_code == 504:
            print(pdef.logcss(gct(),'【upgrade_referral-migrate_data】','error'),'【基础版升级3.0数据迁移】: %s',res.json())
            return ">>>基础版升级3.0数据迁移由于超时导致部分数据迁移失败！", res.json()
        else:
            print(pdef.logcss(gct(),'【upgrade_referral-migrate_data】','error'),'【基础版升级3.0数据迁移】: %s',res.json())
            return ">>>基础版升级3.0数据迁移异常了。"

    # 数据迁移-转介绍2.0升级转介绍3.0
    def migrate_data_2to3(self, company_id, env):
        HOSTS_URI = self.getUri(env)
        req_json = {
            "companyIds": company_id
        }
        short_uri = '/crm-service/migrate/migrateData4at?companyIds=%s' %company_id
        migrate_data_url = f"{HOSTS_URI}"+short_uri
        res = requests.get(migrate_data_url, json=req_json)
        re = res.json()
        # print('【转介绍2.0数据迁移日志】: ',re)
        print(pdef.logcss(gct(),'【upgrade_referral-migrate_data_2to3】'),'【转介绍2.0数据迁移日志】:%s, 入参: %s, 返回数据: %s' %(short_uri,req_json,re))
        if res.status_code == 200 :
            # print(res.headers['x-envoy-upstream-service-time'], )
            if re['code'] == 0 and re['msg'] == '成功':
                return "&nbsp;>>>转介绍2.0升级3.0数据迁移成功啦，用时 % s 毫秒。" % res.headers['x-envoy-upstream-service-time']
            else:
                print(pdef.logcss(gct(),'【upgrade_referral-migrate_data_2to3】'),'【转介绍2.0升级3.0数据迁移】: %s',res.json())
                return "&nbsp;>>>转介绍2.0升级3.0数据迁移失败了！%s" %re
        elif res.status_code == 504:
            print(pdef.logcss(gct(),'【upgrade_referral-migrate_data_2to3】','error'),'【转介绍2.0升级3.0数据迁移】: %s',res.json())
            return "&nbsp;>>>转介绍2.0升级3.0数据迁移由于超时导致部分数据迁移失败！", res.json()
        else:
            print(pdef.logcss(gct(),'【upgrade_referral-migrate_data_2to3】','error'),'【转介绍2.0升级3.0数据迁移】: %s',res.json())
            return "&nbsp;>>>转介绍2.0升级3.0数据迁移异常了。"

    #基础版企业转换为销售工具版企业（未到期的企业转换为团队版，已到期的企业转换为免费版）
    def tosales_tools(self, company_ids, version, env):
        HOSTS_URI = self.getUri(env)
        req_json = {
            "companyIds": company_ids
        }
        if version == 'bs':
            short_uri = '/company-center/company/basic2salesTools' #基础版转销售工具版本
        elif version == 'pd':
            short_uri = '/company-center/company/privateDomain2salesTools' #私域流量池版转销售工具版本
        tosales_url = f"{HOSTS_URI}"+short_uri
        res = requests.post(tosales_url, json=req_json)
        print(pdef.logcss(gct(),'【upgrade_referral-tosales_tools】'),'【基础版合并为销售工具版】:%s, 入参: %s, 返回数据: %s' %(short_uri,req_json,res.json()))
        return res.json()

    #清除app登录token
    def clean_appLoginToken(self, company_id, env):
        HOSTS_URI = self.getUri(env)
        short_uri = f'/loginservice/card/business/applet/cleanAppLoginToken?companyId={company_id}'
        clean_altoken = f"{HOSTS_URI}"+short_uri
        req_json = {}
        try:
            res = requests.post(clean_altoken, json=req_json)
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 502:
                print("❌ 捕获到 502 Bad Gateway 错误")
                # 在这里处理重试逻辑或记录日志
            else:
                print(f"❌ 其他 HTTP 错误: {e}")
                
        except requests.exceptions.RequestException as e:
            # 捕获网络层面的错误 (如连接超时、DNS 失败等)
            print(f"❌ 网络请求失败: {e}")
        print(pdef.logcss(gct(),'【upgrade_referral-clean_appLoginToken】'),'【清除app登录token】:%s, 入参: %s, 返回数据: %s' %(short_uri,req_json,res.json()))
        # print('【】')
        return res.json()

    #激活注销手机号
    def remove_tagTel(self, tel, env):
        HOSTS_URI = self.getUri(env)
        short_uri = '/loginservice/card/app/removeTagTel?tel=%s'%tel
        remove_tagtel = f"{HOSTS_URI}"+short_uri
        print(f"remove_tagTel url: {remove_tagtel}")
        req_json = ''
        try:
            res = requests.post(remove_tagtel, json=req_json)
            res.raise_for_status() 
            print(f"remove_tagTel 成功: {res.json()}")

        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 502:
                print("❌ 捕获到 502 Bad Gateway 错误")
                # 在这里处理重试逻辑或记录日志
            else:
                print(f"❌ 其他 HTTP 错误: {e}")
                
        except requests.exceptions.RequestException as e:
            # 捕获网络层面的错误 (如连接超时、DNS 失败等)
            print(f"❌ 网络请求失败: {e}")
        
        # print(pdef.logcss(gct(),'【upgrade_referral-remove_tagTel】'),f'【激活注销手机号】: {short_uri}, 入参: {req_json}, 返回数据: {res.json()}')
        return res.json()
