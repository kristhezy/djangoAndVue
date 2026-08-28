'''
    1、根据手机号查询企业id和名片;
    2、填入小程序appID;
    3、调用接口开始上传域名和推送版本
    4、配置隐私协议;
    5、提审小程序;
    6、查询审核结果;
    7、发布小程序. 
'''
from. import requests,Colors,HttpResponse
from.publicDef import publicDef as pd

class miniProgram(object):
    def __init__(self):
        self.getappidurl = "/wxauth/wxauth/applet/appid/"
        self.HOSTS_URI_test = 'http://msr.jiatuitest.com'  # 测试
        self.HOSTS_URI_prod = 'http://msr.jtscprod.com'  # 生产
        self.gettokenurl = "/wxauth/token/applet/company?companyId="
        self.mptoken = ""

    #获取日志文本样式
    def logcss(self, time, desc, type="succ"):
        if type == "succ": color = Colors.BLUE
        elif type == "error": color = Colors.RED
        elif type == "warn": color = Colors.YELLOW
        elif type == "green": color = Colors.GREEN
        rlt = f"{Colors.BOLD}{time}{color} {desc}{Colors.RESET}"
        return rlt

    def getURI(self,env):
        if env == 'prod':
            HOSTS_URI = self.HOSTS_URI_prod
        else:
            HOSTS_URI = self.HOSTS_URI_test
        return HOSTS_URI
    
    def getappidbycid(self,companyId,env):
        uri = self.getURI(env) + self.getappidurl + str(companyId)
        try:
            res = requests.get(uri)
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(self.logcss(pd().getctime(),f'miniProgram-getappidbycid: {uri}, 返回数据: {rlt}'))
        return rlt
    
    def gettoken(self,companyId,env):
        uri = self.getURI(env) + self.gettokenurl + str(companyId)
        try:
            res = requests.get(uri)
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(self.logcss(pd().getctime(),f'miniProgram-gettoken: {uri}, 返回数据: {rlt}'))
        self.mptoken = rlt['data']
        
    def wxacommit(self,companyId,env,appId): #上传代码（同时生成体验版）
        self.gettoken(companyId,env)
        uri = f"https://api.weixin.qq.com/wxa/commit?access_token={self.mptoken}"
        data = {
            "template_id": "510",
            "ext_json": "{\"extEnable\":true,\"extAppid\":\"%s\",\"ext\":{\"baseUrl\":\"dsa-app.aijiatui.com\",\"md\":\"%s\",\"companyType\":0,\"token\":2,\"ultimate\":0,\"imAppKey\":\"a941f5923e72b27adc646f2193e76219\"}}"%(appId,companyId),
            "user_version": "v3.10.36",
            "user_desc": "安卓兼容"
        }
        try:
            res = requests.post(url=uri,json=data)
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(self.logcss(pd().getctime(),f'miniProgram-wxacommit: {uri}, 返回数据: {rlt}'))
        return rlt
    
    def setmodifydomain(self): #配置服务器域名
        uri = f"https://api.weixin.qq.com/wxa/modify_domain?access_token={self.mptoken}"
        data = {
            "action": "add",
            "requestdomain": [
                "https://dsa-app.aijiatui.com",
                "https://pingtas.qq.com",
                "https://mall-upyun.aijiatui.com",
                "https://lbs.netease.im",
                "https://wlnimsc0.netease.im",
                "https://wlnimsc1.netease.im",
                "https://dr.netease.im",
                "https://nos.netease.com",
                "https://nim.nosdn.127.net",
                "https://opt-cms.aijiatui.com",
                "https://dsa-business.aijiatui.com",
                "https://resource-1255821078.cos.ap-guangzhou.myqcloud.com",
                "https://apis.map.qq.com",
                "https://vod2.qcloud.com"
            ],
            "wsrequestdomain": [
                "wss://wlnimsc0.netease.im",
                "wss://wlnimsc1.netease.im"
            ],
            "uploaddomain": [
                "https://nos.netease.com",
                "https://nim.nosdn.127.net",
                "https://resource-1255821078.cos.ap-guangzhou.myqcloud.com",
                "https://vod2.qcloud.com",
                "https://mall-upyun.aijiatui.com",
                "https://dsa-app.aijiatui.com",
                "https://saas-static-1255821078.cos.ap-guangzhou.myqcloud.com"
            ],
            "downloaddomain": [
                "https://nim.nosdn.127.net",
                "https://resource.aijiatui.com",
                "https://p.qlogo.cn",
                "https://wx.qlogo.cn",
                "https://thirdwx.qlogo.cn",
                "https://cos-jiajiao.aijiatui.com",
                "https://dsa-business.aijiatui.com",
                "https://vod-qcloud.aijiatui.com",
                "https://mall-upyun.aijiatui.com",
                "https://dsa-app.aijiatui.com",
                "https://saas-static.aijiatui.com",
                "https://vod-ugc.aijiatui.com",
                "https://vipopdev-cdn.aijiatui.com"
            ]
        }
        try:
            res = requests.post(url=uri,json=data)
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(self.logcss(pd().getctime(),f'miniProgram-setmodifydomain23: {uri}, 返回数据: {rlt}'))
        return rlt
    
    def setwebviewdomain(self): #配置业务域名
        uri = f"https://api.weixin.qq.com/wxa/setwebviewdomain_directly?access_token={self.mptoken}"
        data = {
            "action": "add",
            "webviewdomain": [
                "https://dsa-app.aijiatui.com"
            ]
        }
        try:
            res = requests.post(url=uri,json=data)
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(self.logcss(pd().getctime(),f'miniProgram-setwebviewdomain: {uri}, 返回数据: {rlt}'))
        return rlt
    
    def get_webviewdomain_confirmfile(self): #获取业务域名校验文件
        uri = f"https://api.weixin.qq.com/wxa/get_webviewdomain_confirmfile?access_token={self.mptoken}"
        data = {}
        try:
            res = requests.post(url=uri,json=data)
            status = res.status_code
            if status == 200:
                rlt = res.json()   
                print(self.logcss(pd().getctime(),f'miniProgram-get_webviewdomain_confirmfile: {uri}, 返回数据: {rlt}'))
                return rlt  # 或 response.text，依接口而定
            elif status == 400: print("❌ 客户端错误：请求格式不正确（400 Bad Request）")
            elif status == 401: print("❌ 未授权：缺少或无效的认证信息（401 Unauthorized）")
            elif status == 403: print("❌ 禁止访问：无权限上传文件（403 Forbidden）")
            elif status == 404: print("❌ 接口未找到（404 Not Found）——请检查上传 URL 是否正确")
            elif status == 413: print("❌ 文件过大，服务器拒绝处理（413 Payload Too Large）")
            elif status == 500: print("💥 服务器内部错误（500 Internal Server Error）")
            elif status == 502 or status == 503: print(f"⚠️ 服务暂时不可用（{status}）")
            else: print(f"⚠️ 未知响应状态码：{status}")
        except requests.exceptions.Timeout: print("⏰ 请求超时，请检查网络或服务器状态")
        except requests.exceptions.ConnectionError: print("🔌 网络连接错误，请检查 URL 或网络")
        except requests.exceptions.RequestException as e: print(f"🚨 请求发生未知错误: {e}")
        except Exception as e: print(f"💥 意外错误: {e}")
    
    def getcategory(self,companyId,env): #获取小程序的类目
        self.gettoken(companyId,env)
        uri = f"https://api.weixin.qq.com/cgi-bin/wxopen/getcategory?access_token={self.mptoken}"
        print("getcategory-uri:",uri)
        try:
            res = requests.get(url=uri)
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(self.logcss(pd().getctime(),f'miniProgram-getcategory: {uri}, 返回数据: {rlt}'))
        return rlt

    def wxasubaudit(self,items,companyId,env): #提审小程序
        self.gettoken(companyId,env)
        uri = f"https://api.weixin.qq.com/wxa/submit_audit?access_token={self.mptoken}"
        data = {
            "privacy_api_not_use":True,
            "item_list":items,
            "ugc_declare": {
                "scene": [0]
            }
        }
        try:
            res = requests.post(url=uri,json=data)
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(self.logcss(pd().getctime(),f'miniProgram-wxasubaudit: {uri}, 入参:{data}, 返回数据: {rlt}'))
        return rlt
    
    def getauditstatus(self,companyId,env): #查询小程序审核状态
        self.gettoken(companyId,env)
        uri = f"https://api.weixin.qq.com/wxa/get_latest_auditstatus?access_token={self.mptoken}"
        print("getauditstatus-uri:",uri)
        try:
            res = requests.get(url=uri)
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(self.logcss(pd().getctime(),f'miniProgram-getauditstatus: {uri}, 返回数据: {rlt}'))
        return rlt
    
    def wxarelease(self,companyId,env): #发布小程序
        self.gettoken(companyId,env)
        uri = f"https://api.weixin.qq.com/wxa/release?access_token={self.mptoken}"
        data = {}
        try:
            res = requests.post(url=uri,json=data)
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(self.logcss(pd().getctime(),f'miniProgram-wxarelease: {uri}, 返回数据: {rlt}'))
        return rlt

    def undocodeaudit(self,companyId,env): #撤回审核
        self.gettoken(companyId,env)
        uri = f"https://api.weixin.qq.com/wxa/undocodeaudit?access_token={self.mptoken}"
        try:
            res = requests.get(url=uri)
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(self.logcss(pd().getctime(),f'miniProgram-undocodeaudit: {uri}, 返回数据: {rlt}'))
        return rlt
    
    def bindtester(self,wechatid,companyId,env): #绑定体验者
        self.gettoken(companyId,env)
        uri = f"https://api.weixin.qq.com/wxa/bind_tester?access_token={self.mptoken}"
        data = {"wechatid": wechatid}
        try:
            res = requests.post(url=uri, json=data)
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(self.logcss(pd().getctime(),f'miniProgram-bindtester: {uri} 返回数据: {rlt}'))
        return rlt #{"errcode": 0,"errmsg": "ok","userstr": "3558036015b771cb498ebf80ff486ea182a0a1eae8d13f012fc07a600ad3b56f"}
    
    def unbindtester(self,wechatid,companyId,env): #解绑体验者
        self.gettoken(companyId,env)
        uri = f"https://api.weixin.qq.com/wxa/unbind_tester?access_token={self.mptoken}"
        data = {"wechatid": wechatid}
        try:
            res = requests.post(url=uri, json=data)
            rlt = res.json()
        except Exception as e:
            rlt = e
        print(self.logcss(pd().getctime(),f'miniProgram-unbindtester: {uri} 返回数据: {rlt}'))
        return rlt
    
    def getqrcode(self,companyId,env): #获取体验码
        self.gettoken(companyId,env)
        uri = f"https://api.weixin.qq.com/wxa/get_qrcode?access_token={self.mptoken}"
        try:
            res = requests.get(url=uri)
            res.raise_for_status()
            rlt = res.content
        except Exception as e:
            rlt = e
        print(self.logcss(pd().getctime(),f'miniProgram-getqrcode: {uri} 返回数据: {rlt}'))
        return rlt

    def errorcode(self,errcode):
        ec = str(errcode)
        rlt = ""
        #业务域名
        if ec == "40001": rlt = "获取 access_token 时 AppSecret 错误，或者 access_token 无效。"
        elif ec == "89019": rlt = "业务域名无更改，无需重复设置。"
        elif ec == "89020": rlt = "尚未设置小程序业务域名，请先在第三方平台中设置小程序业务域名后在调用本接口"
        elif ec == "89021": rlt = "请求保存的域名不是第三方平台中已设置的小程序业务域名或子域名"
        elif ec == "89029": rlt = "业务域名数量超过限制，最多可以添加300个业务域名。"
        elif ec == "89231": rlt = "个人小程序不支持调用 setwebviewdomain 接口。"
        #服务器域名
        elif ec == "-1": rlt = "系统繁忙，此时请开发者稍候再试"
        elif ec == "40001": rlt = "获取 access_token 时 AppSecret 错误，或者 access_token 无效。"
        elif ec == "40014": rlt = "不合法的 access_token。"
        elif ec == "85015": rlt = "该账号不是小程序账号。"
        elif ec == "85017": rlt = "域名输入为空，或者没有新增域名。"
        elif ec == "85018": rlt = "域名没有在第三方平台设置。"
        elif ec == "85301": rlt = "存在 “不符合域名规则的域名”导致无修改。"
        elif ec == "85302": rlt = "存在 “ 缺少ICP备案的域名”导致无修改。"
        elif ec == "85303": rlt = "同时存在“不符合域名规则的域名”以及“ 缺少ICP备案的域名”导致无修改。"
        #查询校验文件
        elif ec == "44002": rlt = "POST 的数据包为空。post请求body参数不能为空。"
        elif ec == "85058": rlt = "不存在有效的审核信息"
        #提交审核
        elif ec == "47001": rlt = "数据格式错误"
        elif ec == "61040": rlt = "请先配置隐私接口权限。"
        elif ec == "85006": rlt = "标签格式错误"
        elif ec == "85007": rlt = "页面路径错误	"
        elif ec == "85008": rlt = "当前小程序没有已经审核通过的类目，请添加类目成功后重试"
        elif ec == "85009": rlt = "已经有正在审核的版本"
        elif ec == "85010": rlt = "类目item_list 有项目为空"
        elif ec == "85011": rlt = "标题填写错误"
        elif ec == "85023": rlt = "审核列表填写的项目数不在 1-5 以内"
        elif ec == "85051": rlt = "version_desc或者preview_info超限"
        elif ec == "85077": rlt = "小程序类目信息失效（类目中含有官方下架的类目，请重新选择类目）"
        elif ec == "85085": rlt = "小程序提审数量已达本月上限"
        elif ec == "85086": rlt = "提交代码审核之前需提前上传代码"
        elif ec == "85087": rlt = "小程序已使用 api navigateToMiniProgram，请声明跳转 appid 列表后再次提交"
        elif ec == "85092": rlt = "preview_info格式错误"
        elif ec == "85093": rlt = "preview_info 视频或者图片个数超限"
        elif ec == "85094": rlt = "需提供审核机制说明信息"
        elif ec == "86000": rlt = "不是由第三方代小程序进行调用"
        elif ec == "86001": rlt = "不存在第三方的已经提交的代码"
        elif ec == "86002": rlt = "小程序还未设置昵称、头像、简介。请先设置完后再重新提交"
        elif ec == "86007": rlt = "小程序禁止提交"
        elif ec == "86009": rlt = "服务商新增小程序代码提审能力被限制"
        elif ec == "86010": rlt = "服务商迭代小程序代码提审能力被限制"
        elif ec == "87006": rlt = "小游戏不能提交"
        elif ec == "9400001": rlt = "该开发小程序已开通小程序直播权限，不支持发布版本。" 
        elif ec == "9402202": rlt = "请勿频繁提交，待上一次操作完成后再提交" 
        #发布
        elif ec == "85019": rlt = "没有审核版本"
        elif ec == "85020": rlt = "审核状态未满足发布"
        elif ec == "87013": rlt = "撤回次数达到上限（每天5次，每个月 10 次）"
        #绑定体验者
        elif ec == "85001": rlt = "微信号不存在或微信号设置为不可搜索"
        elif ec == "85002": rlt = "小程序绑定的体验者数量达到上限"
        elif ec == "85003": rlt = "微信号绑定的小程序体验者达到上限"
        elif ec == "85004": rlt = "微信号已经绑定"

        return rlt



from django.http import HttpResponse #type: ignore
import csv
from urllib.parse import quote  # 解决中文文件名乱码
from datetime import datetime

def download_dynamic_file(request):
    # 1. 接收前端传递的参数（支持GET/POST，根据需求选择）
    # GET方式：从URL参数获取（如 /download/?type=user&date=20251225）
    file_type = request.GET.get('type', 'txt')  # 文件类型（默认txt）
    filter_date = request.GET.get('date', datetime.now().strftime("%Y%m%d"))  # 筛选日期
    custom_name = request.GET.get('name', '动态文件')  # 自定义文件名
    file_content = request.GET.get('content', '文件内容')  # 自定义文件内容
    
    # POST方式：从表单/JSON获取（若参数较多/敏感，推荐POST）
    # filter_data = request.POST.get('filter_data')  # 示例：POST参数

    # 2. 校验参数（可选，防止非法参数）
    if file_type not in ['csv', 'txt', 'json']:
        return HttpResponse("不支持的文件类型", status=400)

    # 3. 根据参数动态生成文件内容
    if file_type == 'csv':
        # 构造CSV响应（指定MIME类型）
        response = HttpResponse(content_type='text/csv')
        # 设置下载文件名（解决中文乱码）
        filename = f"{custom_name}_{filter_date}.csv"
        response['Content-Disposition'] = f'attachment; filename="{quote(filename)}"'
        
        # 写入CSV内容（模拟根据参数查询数据库/生成数据）
        writer = csv.writer(response)
        # 表头（可根据参数动态调整）
        writer.writerow(['ID', '名称', '日期', '类型'])
        # 模拟数据（实际可从数据库查询，参数作为筛选条件）
        for i in range(5):
            writer.writerow([i+1, f"数据{i+1}", filter_date, file_type])
    
    elif file_type == 'txt':
        # 生成TXT文件
        response = HttpResponse(content_type='text/plain')
        filename = f"{custom_name}"
        response['Content-Disposition'] = f'attachment; filename="{quote(filename)}"'
        # 动态拼接TXT内容
        content = file_content
        response.write(content)
    
    elif file_type == 'json':
        # 生成JSON文件
        import json
        response = HttpResponse(content_type='application/json')
        filename = f"{custom_name}_{filter_date}.json"
        response['Content-Disposition'] = f'attachment; filename="{quote(filename)}"'
        # 动态构造JSON数据
        json_data = {
            "title": custom_name,
            "date": filter_date,
            "data": [{"id": i+1, "name": f"数据{i+1}"} for i in range(5)]
        }
        response.write(json.dumps(json_data, ensure_ascii=False, indent=2))

    # 4. 返回响应，触发浏览器下载
    return response