from. import logger,JsonResponse as jr,json,redirect,pub_utils as pu,re,login_required,never_cache,cache_page,time,Colors,current_dir
from.ov_setting import OVSetting,pdef
from.mmeett import mmeettIF
from.xcard import xcard
from.config.codemess import masseges as m, codes as c
from.pub_SqlTool import mySqlPool

# ── 懒加载（首次调用才实例化，避免拖慢 Django 启动）──
_ovs = None
_mif = None
_xc = None

def _get_ovs():
    global _ovs
    if _ovs is None: _ovs = OVSetting()
    return _ovs

def _get_mif():
    global _mif
    if _mif is None: _mif = mmeettIF()
    return _mif

def _get_xc():
    global _xc
    if _xc is None: _xc = xcard()
    return _xc

msp = mySqlPool  # mySqlPool 只是类别名，不需要实例化
msr = [' msr&eureka: 华为云 ','2','私有化部署','3']
mmeett_regist_log = current_dir / "djangoPlant/configFile/mmeettRegist.json"

def _log_mmeett_regist(rcode, uname, pwd, country, env):
    """记录 mmeett 注册信息（邀请码、账号、密码、地区、注册时间）"""
    import json as _json
    record = {
        "rcode": rcode, "uname": uname, "pwd": pwd,
        "country": country, "env": env, "register_time": pdef.getctime(),
    }
    try:
        log_data = []
        if mmeett_regist_log.exists():
            with open(mmeett_regist_log, 'r', encoding='utf-8') as f:
                log_data = _json.load(f)
        log_data.append(record)
        with open(mmeett_regist_log, 'w', encoding='utf-8') as f:
            _json.dump(log_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[mmeett_regist_log] 写入失败: {e}")

def _del_mmeett_regist(uname, pwd):
    """注销成功时，用账号密码匹配 regist log，匹配上就删除"""
    import json as _json
    try:
        if not mmeett_regist_log.exists():
            return
        with open(mmeett_regist_log, 'r', encoding='utf-8') as f:
            log_data = _json.load(f)
        new_data = [r for r in log_data if not (r.get("uname") == uname and r.get("pwd") == pwd)]
        if len(new_data) < len(log_data):
            with open(mmeett_regist_log, 'w', encoding='utf-8') as f:
                _json.dump(new_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[mmeett_regist_log] 删除失败: {e}")

def _log_mmeett_op(request, data, resp):
    """记录 mmeett 操作日志（供 Agent 汇总）。从返回的 JsonResponse 解析 code/msg/data"""
    try:
        action = data.get("type", "")
        env = data.get("env", "test")
        uid = request.session.get("uid", 0)
        uname = request.session.get("uname", "")
        code, msg, rlt = "", "", ""
        if resp is not None and hasattr(resp, "content"):
            try:
                body = json.loads(resp.content.decode("utf-8"))
                code = body.get("code", "")
                msg = body.get("msg", "")
                rlt = body.get("data", "")
            except Exception:
                pass
        success = 1 if (code == 0 or code == "0") else 0
        params = json.dumps({k: v for k, v in data.items() if k != "type"}, ensure_ascii=False, default=str)
        pu.iaq.inst_mmeett_op_log(uid, uname, env, action, params, str(rlt)[:2000], success)
    except Exception as e:
        print(f"[mmeett_op_log] 记录失败: {e}")

VERSION_MAP = {3: '基线版', 4: 'soon', 5: '老meet', 6: '通威版', 7: 'mmeett'}
COUNTRY_CODE_MAP = {
    '3630979328926009': 'JP',
    '3630979328926013': 'TW',
    '3630979328925988': 'ID',
    '3630979328926003': 'TH',
    "3630979328925990": "SG",
    "3630979328925992": "MY",
}
VIP_LEVEL_MAP = {0: '非会员', 1: '金级会员', 2: '白金会员', 3: '银级会员'}
CS_STATUS_MAP = {0: '禁用', 1: '正常', 2: '注销'}
PV_VERSION_MAP = {'1': 'Pro', '2': 'Premium', '3': 'Pro', '4': 'Premium'}
DURATION_TYPE_MAP = {'0': '会议转录', '1': 'AI翻译'}

def gct():
    return pdef.getctime()

def generate_username(prefix, start_num, index, suffix='', width=0):
    num = start_num + index
    if num == 0:
        base = prefix
    else:
        base = prefix + (str(num).zfill(width) if width > 0 else str(num))
    return base + suffix if suffix else base

def check_login(request):
    return request.session.get("isLoggedIn")

def build_response(code, msg, result):
    return jr(pdef.get_result(code, msg, result))

def setColor(content):
    rlt = f"{Colors.RED}{Colors.BOLD}{content}{Colors.RESET}"
    return rlt

def _getLevelLoction(location_list):
    # 第一步：找最小的 nodeLevel
    min_node = int(min(d['nodeLevel'] for d in location_list))
    # 第二步：从 nodeLevel 最小的记录中，再找最小的 side
    min_side = int(min(d['side'] for d in location_list if int(d['nodeLevel']) == min_node))
    # 第三步：筛选出同时满足两个最小值的记录
    min_rlt = [d for d in location_list if int(d['nodeLevel']) == min_node and int(d['side']) == min_side]
    return min_rlt
 
@login_required
@never_cache
def mmeettopen(request):
    return redirect('/')

@never_cache
def pmmeett_action(request, action):
    """action 从 URL 路径获取"""
    data = json.loads(request.body)
    data["type"] = action
    resp = _process_pmmeett(request, data)
    _log_mmeett_op(request, data, resp)
    return resp

def _process_pmmeett(request, data):
    print(f'【{gct()}】--  "MMEETT"')
    action = data["type"]
    print(f"action: {action}")
    env = data.get("env", "test")
    version = data.get("version", 7)
    uname = data.get("uname", "")
    emailSuffix = data.get("emailSuffix", "@jt.com")
    rlt = ""
    code,msg = "",""

    if action == "mmeettRegist":
        mset = data["mset"]
        rcode = data["rcode"]
        pwd = data["pwd"]
        repwd = data["repwd"]
        country = data["country"]
        bemail = data["bemail"]
        paypwd = data["paypwd"]
        unum = data["unum"]
        prefix, start_num, suffix, num_width = pdef.extract_prefix_and_number(uname)
        if mset == "bemaspp": unum = 1
        try:
            for i in range(int(unum)):
                uname = generate_username(prefix, start_num, i, suffix, num_width)
                if suffix: email = uname
                else: email = uname + emailSuffix
                if mset == "regist":
                    mrnrlt = _get_mif().mmeettRegistNew(uname, pwd, repwd, country, rcode, env, version)
                    ulrlt = {"code": "", "msg": ""}
                else:
                    ulrlt = _get_mif().userlogin(uname, env, version)
                    mrnrlt = {"code": "", "msg": ""}
                if mrnrlt["code"] == 0 or ulrlt["code"] == 0:
                    # ── 注册成功时记录日志 ──
                    if mset == "regist" and mrnrlt.get("code") == 0:
                        _log_mmeett_regist(rcode, uname, pwd, country, env)
                    uinfo = _get_mif().queryUserInfo(email, env, version)
                    uid = uinfo['data']['user']['jtUserId']
                    urcode = uinfo['data']['user']['referralCode']
                    rlt += f"账号: {uname}, userId: {uid}, 推荐码: {urcode}. " if mset == "regist" else f"账号 {uname} 设置结果: "
                    if mset == "regist" and env == "test": #注册时安置用户
                        gtrlt = _get_mif().getTree(env, version)
                        if not gtrlt['data']['placementParentReferralCode']:
                            uinfo = _get_mif().queryUserInfo(email,env,version)
                            userId = uinfo["data"]["user"]["jtUserId"]
                            glirlt = _get_mif().getLocationInfo(userId,env,version)
                            if glirlt["code"] == 0:
                                location_list = glirlt.get("data", [])
                                if not location_list:
                                    rlt += f"安置失败，未获取到安置位置信息."
                                else:
                                    min_rlt = _getLevelLoction(location_list)
                                    upperUserId = min_rlt[0]['userId']
                                    side = min_rlt[0]['side']
                                    uhrlt = _get_mif().updateHierarchy(upperUserId, userId, side,env,version)
                                    if uhrlt['code'] == -8057:
                                        rlt += f"安置失败，上级还未被安置."
                                        stop = 1
                                    elif uhrlt['code'] == 0: rlt += f"安置成功！"
                            else:
                                rlt += glirlt['msg']
                        else: 
                            rlt +=  f"无需重复安置."
                    if bemail == "yes" and env == "test": #绑定邮箱
                        sendcode = _get_mif().sendEmail(env, version, 12, country)
                        if sendcode["code"] == 0:
                            time.sleep(0.5)
                            bemrlt = _get_mif().bindAppEmail(env, version)
                            rlt += f"绑定邮箱「{email}」{'成功. ' if bemrlt['code'] == 0 else '失败, ' + bemrlt['msg']}"
                        elif sendcode["code"] == -106:
                            rlt += f"邮箱「{email}」已被绑定！"
                        else:
                            rlt += "「绑定邮箱」验证码发送失败。"
                    if len(paypwd) == 6 and env == "test": #设置支付密码
                        sendcode = _get_mif().sendEmail(env, version, 6)
                        if sendcode["code"] == 0:
                            upprlt = _get_mif().updatePayPwd(env, version, paypwd)
                            rlt += f"修改支付密码{'成功. ' if upprlt['code'] == 0 else '失败, ' + upprlt['msg']}"
                        else:
                            rlt += "「修改支付密码」邮箱验证码发送失败。"
                    if mrnrlt["code"] == 0:
                        code = mrnrlt["code"]
                        msg = mrnrlt["msg"]
                    if ulrlt["code"] == 0:
                        code = ulrlt["code"]
                        msg = ulrlt["msg"]
                else:
                    if mrnrlt["msg"]:
                        code = mrnrlt["code"]
                        msg = mrnrlt["msg"]
                        rlt += f'{uname}, {mrnrlt["msg"]}!'
                    if ulrlt["msg"]:
                        code = ulrlt["code"]
                        msg = ulrlt["msg"]
                        rlt += f'{uname}, {ulrlt["msg"]}!'
                rlt += "<br/>"
        except Exception as e:
            print(f"{setColor('⚠️ mmeettRegist 任务因接口异常中断:')} {e}")
            return

    elif action == "getRechargeConfig":
        email = uname + emailSuffix
        rcids = (1, 3, 5, 7, 9, 30, 33, 35, 37, 39, 41, 43, 45, 47)
        ulrlt = _get_mif().userlogin(uname, env, version)
        if ulrlt["code"] == 0:
            uinfo = _get_mif().queryUserInfo(email, env, version)
            ulevel = uinfo["data"]["user"]["memberKind"]
            rcrlt = _get_mif().rechargeConfig(env, version)
            rcnd = [i for i in rcrlt["data"] for j in rcids if j == i["id"] and ulevel != i["level"]]
            print(f"getRechargeConfig: {rcnd}")
            code = rcrlt['code']
            msg = rcrlt['msg']
            rlt = rcnd
        else:
            code = ulrlt['code']
            msg = ulrlt['msg']
            rlt = ulrlt['msg']

    elif action == "demotionVip": #会员降级
        level = data["level"]
        email = uname + emailSuffix
        ulrlt = _get_mif().userlogin(uname, env, version)
        if ulrlt["code"] == 0:
            uinfo = _get_mif().queryUserInfo(email, env, version)
            userId = uinfo["data"]["user"]["jtUserId"]
            leveln = VIP_LEVEL_MAP.get(int(level), "未知")
            # _get_mif().loginAdmin(env)
            dvrlt = _get_mif().demotionVip(userId, level, env, version)
            if dvrlt['code'] == 0:
                code = dvrlt['code']
                msg = dvrlt['msg']
                rlt = f"用户「{uname}」降级为「{leveln}」！"
            else:
                code = dvrlt['code']
                msg = dvrlt['msg']
                rlt = f"用户「{uname}」降级失败，原因：{dvrlt['msg']}. "
        else:
            code = ulrlt['code']
            msg = ulrlt['msg']
            rlt = ulrlt['msg']

    elif action == "buyVip": #购买会员
        rcinfo = data["rcinfo"]
        levelId = data["level"]
        unum = data["unum"]
        sknums = []
        for i in rcinfo:
            if int(levelId) == int(i["id"]):
                discountedPrice = i["discountedPrice"]
                print(f"pmmeett-buyVip: rcinfo={i}")
                if i["productVOList"]:
                    for j in i["productVOList"]:
                        pskus = {"productId": j["id"],"skuId": j["productSkus"][0]["skuId"],"quantity": j["num"]}
                        sknums.append(pskus)
        print(f"pmmeett-buyVip: sknums={sknums}")
        prefix, start_num, suffix, num_width = pdef.extract_prefix_and_number(uname)
        for j in range(int(unum)):
            uname = generate_username(prefix, start_num, j, suffix, num_width)
            if suffix: email = uname
            else: email = uname + emailSuffix
            ul = _get_mif().userlogin(uname, env, version)
            if ul["code"] != 0:
                rlt += f"用户 {uname} 登录失败: {ul['msg']}; "
                continue
            _get_mif().sendEmail(env, version, 12, "")
            _get_mif().bindAppEmail(env, version)
            uinfo = _get_mif().queryUserInfo(email, env, version)
            userId = uinfo["data"]["user"]["jtUserId"]
            validAmt = uinfo["data"]["user"]["validAmt"]
            # msp("mmeett", "wecard").execute("update user_vip_info set valid_amt = 9999900 where user_id = %s;", userId)
            if validAmt < discountedPrice:
                acrlt = _get_mif().assetChange(userId,"9999900","1",env,version)
                if acrlt["code"] != 0: return build_response(acrlt["code"], acrlt["msg"], acrlt["msg"])
            mprlt = _get_mif().purchase(levelId, sknums, env, version)
            if mprlt["code"] == 0:
                pmid = mprlt["data"]
                porlt = _get_mif().paymentOrder(pmid, env, version)
                subject = porlt["data"]["orderName"]
                prrlt = _get_mif().paymentRequest(pmid, subject, env, version)
                if prrlt["code"] == 0:
                    code = c['success']
                    msg = m['success']
                    rlt += f"用户{uname}购买会员成功！"
                else:
                    code = prrlt["code"]
                    msg = prrlt["msg"]
                    rlt += f"用户{uname}购买会员失败，原因：{prrlt['msg']}"
            else:
                code = mprlt["code"]
                msg = mprlt["msg"]
                rlt += f"用户「{uname}」获取订单ID失败，原因{mprlt}. "
            # rlt += uhr
            rlt += "<br/>"

    elif action in ("queryRCode","queryUserName","queryUserEmail"): #查询用户邀请码和地区
        email = uname + emailSuffix
        ul = _get_mif().userlogin(uname, env, version)
        if ul["code"] != 0: return build_response(ul["code"], ul["msg"], ul["msg"])
        uinfo = _get_mif().queryUserInfo(email, env, version)
        if action == "queryRCode": #查询用户邀请码和地区
            rcode = uinfo["data"]["user"]["referralCode"]
            country = uinfo["data"]["user"]["countryCode"]
            rlt = {"rcode": rcode, "country": country}
        elif action == "queryUserName": #查询用户名
            rlt = {"userName": uinfo["data"]["user"].get("nickname", "")}
        elif action == "queryUserEmail": #查询用户邮箱
            rlt = {"email": uinfo["data"]["user"].get("email", "")}
        code = uinfo['code']
        msg = uinfo['msg']

    elif action == "mmeettAddReferralLinks": #生成邀请链路
        rcode = data["rcode"]
        country = data["country"]
        level = data["level"]
        unum = data["unum"]
        prefix, start_num, suffix, num_width = pdef.extract_prefix_and_number(uname)
        for i in range(int(unum)):
            newuname = generate_username(prefix, start_num, i, suffix, num_width)
            print(f"before request rigestAndOpenVip: rcode={rcode}, country={country}, level={level}")
            nrcode, raovrlt = _get_mif().rigestAndOpenVip(i, newuname, rcode, country, level, env, version)
            if nrcode:
                rcode = nrcode
            rlt += str(raovrlt)
        code = c['success']
        msg = m['success']

    elif action == "updateUserInfo": #修改用户国家/地区、用户名、邮箱
        country = data['country']
        userName = data['userName']
        userEmail = data['userEmail']
        ccode = COUNTRY_CODE_MAP.get(country, "")
        email = uname + emailSuffix
        ul = _get_mif().userlogin(uname, env, version)
        if ul["code"] != 0: return build_response(ul["code"], ul["msg"], ul["msg"])
        uinfo = _get_mif().queryUserInfo(email, env, version)
        userId = uinfo["data"]["user"]["jtUserId"]
        # _get_mif().loginAdmin(env)
        rlt = f"用户「{uname}」"
        if country:
            kw = {"countryCode": ccode}
            uuirlt = _get_mif().updateUserInfo(userId, env, version, **kw)
            if uuirlt['code'] == 0:
                rlt += f"修改国家/地区为「{ccode}」！"
            else:
                rlt += f"修改国家/地区失败，原因：{uuirlt['msg']}"
        if userName:
            kw = {"account":userName, "userName":userName}
            uuirlt = _get_mif().updateUserInfo(userId, env, version, **kw)
            if uuirlt['code'] == 0:
                rlt += f"修改用户名为「{userName}」！"
            else:
                rlt += f"修改用户名失败，原因：{uuirlt['msg']}"
        if userEmail:
            kw = {"email":userEmail}
            uuirlt = _get_mif().updateUserInfo(userId, env, version, **kw)
            if uuirlt['code'] == 0:
                rlt += f"修改邮箱为「{userEmail}」！"
            else:
                rlt += f"修改邮箱失败，原因：{uuirlt['msg']}"
        code = c['success']
        msg = m['success']

    elif action == "queryCountryInfo":
        rcirlt = _get_mif().queryCountryInfo(env,version)
        rlt = []
        for i in rcirlt["data"]:
            kv = {"value":i["id"],"name":i["name"]}
            rlt.append(kv)
        code = rcirlt['code']
        msg = rcirlt['msg']

    elif action == "runReward": #奖励重跑
        rerunMode = data['rerunMode']
        print(f"runReward-rerunMode: {rerunMode}")
        rewardType = data['rewardType']
        stime = data['startTime']
        startTime = str(stime) + " 15:00:00"
        etime = data['endTime']
        endTime = str(etime) + " 14:59:59"
        types = data['types']
        rtdict = {27:"感恩分红奖", 28:"推荐奖", 29:"分享奖", 30:"安置奖", 31:"层碰奖", 32:"级差奖", 33:"级差对等奖", 35:"全球分红",43:"集团奖励分红"}
        rtn = rtdict.get(int(rewardType), "")
        rrlt =''
        rrm = []
        if "detail" in types:
            isPre = 0
            drrltt = _get_mif().dataRange(startTime,endTime,rewardType,isPre,env,version)
            if drrltt['code'] == 0: rrlt += f"‘明细’、"
        if "pre" in types:
            isPre = 1
            drrlt = _get_mif().dataRange(startTime,endTime,rewardType,isPre,env,version)
            if drrlt['code'] == 0: rrlt += f"‘预结算’、"
        if "summary" in types:
            if rerunMode and int(rewardType) == 43:
                for i in rerunMode:
                    print(f"runReward-rerunMode-i: {i}")
                    if int(i) == 1: rrm.append('周结')
                    elif int(i) == 2: rrm.append('月结')
                    drsrlt = _get_mif().dataRangeSummary(startTime,endTime,rewardType,env,version,int(i))
                rrlt += f"‘汇总’-{rrm}"
            else:
                drsrlt = _get_mif().dataRangeSummary(startTime,endTime,rewardType,env,version)
                if drsrlt['code'] == 0: rrlt += f"‘汇总’"
        rlt = f"【{gct()}】「{rtn}」({startTime} ~ {endTime}): {rrlt} 执行完成！"
        code = c['success']
        msg = m['success']

    elif action == "queryComputingList": #获取算力列表
        computingNames = {}
        # _get_mif().loginAdmin(env)
        qclrlt = _get_mif().getComputingRechargeConfigList(env,version)
        print(f"originview-queryComputingList: {qclrlt}")
        if qclrlt["code"] != 0:
            rlt = qclrlt.get("msg", "获取算力列表失败")
            code = qclrlt["code"]
            msg = qclrlt.get("msg", "")
        else:
            clist = qclrlt["data"]
            for i in clist:
                computingNames[int(i['id'])] = int(i['computingCnt']) + int(i['giftComputingCnt'])
            clist.append({"id": 0,"name": "自定义"})
            rlt = {"clist":clist,"computingNames":computingNames}
            code = c['success']
            msg = m['success']

    elif action == "sendComputing": #发放算力值
        ccnt = data['computingNum']
        sendAward = data['sendAward']
        computingType = data['computingType']
        computingNames = data['computingNames']
        ccntlist = data['ccntlist']
        email = uname + emailSuffix
        ul = _get_mif().userlogin(uname,env,version)
        if ul["code"] != 0: return build_response(ul["code"], ul["msg"], ul["msg"])
        uinfo = _get_mif().queryUserInfo(email,env,version)
        userId = uinfo["data"]["user"]["jtUserId"]
        # _get_mif().loginAdmin(env)
        scrlt = _get_mif().sendComputing(computingType,userId,sendAward,ccntlist,env,version,ccnt)
        computingNames["0"] = ccnt
        # print(f"【sendComputing】：computingType={computingType}, computingNames={computingNames},computingNames类型={type(computingNames)}")
        cnt = computingNames.get(str(computingType),"")
        if scrlt['code'] == 0:
            rlt = f"用户「{uname}」充值了「{cnt}」算力值."
        else: rlt=scrlt['msg']
        code = scrlt['code']
        msg = scrlt['msg']

    elif action == "computingConsumption":
        amount = data["amount"]
        email = uname + emailSuffix
        ul = _get_mif().userlogin(uname,env,version)
        if ul["code"] != 0: return build_response(ul["code"], ul["msg"], ul["msg"])
        uinfo = _get_mif().queryUserInfo(email,env,version)
        userId = uinfo["data"]["user"]["jtUserId"]
        ccrlt = _get_mif().computingConsumption(userId,amount,env,version)
        if ccrlt['code'] == 0: rlt = f"用户「{uname}」扣减算力『{amount}』."
        else: rlt=ccrlt['msg']
        code = ccrlt['code']
        msg = ccrlt['msg']

    elif action == "userSettle": #安置
        isBatch = data["isBatch"]
        uhr = ""
        stop = 0
        prefix, start_num, suffix, num_width = pdef.extract_prefix_and_number(uname)
        if suffix: email = uname
        else: email = uname + emailSuffix
        ul = _get_mif().userlogin(uname,env,version)
        if ul['code'] == 43266:
            uhr += f"用户「{email}」不存在. <br/>"
            msg = ul['msg']
            code = ul['code']
        elif ul['code'] == -15:
            uhr += f"用户「{email}」密码错误. <br/>"
            msg = ul['msg']
            code = ul['code']
        elif ul['code'] == 0:
            gtrlt = _get_mif().getTree(env,version)
            if not gtrlt['data']['placementParentReferralCode']:
                # _get_mif().loginAdmin(env)
                uinfo = _get_mif().queryUserInfo(email,env,version)
                userId = uinfo["data"]["user"]["jtUserId"]
                glirlt = _get_mif().getLocationInfo(userId,env,version)
                if glirlt["code"] == 0:
                    location_list = glirlt.get("data", [])
                    if not location_list:
                        uhr += f"「{email}」安置失败，未获取到安置位置信息. <br/>"
                        stop = 1
                    else:
                        min_rlt = _getLevelLoction(location_list)
                        upperUserId = min_rlt[0]['userId']
                        side = min_rlt[0]['side']
                        uhrlt = _get_mif().updateHierarchy(upperUserId, userId, side,env,version)
                        if uhrlt['code'] == -8057:
                            uhr += f"「{email}」安置失败，你的上级还未被安置. <br/>"
                            stop = 1
                        elif uhrlt['code'] == 0: uhr += f"「{email}」安置成功！<br/>"
                        msg = uhrlt['msg']
                        code = uhrlt['code']
                else:
                    uhr = glirlt['msg']
                    msg = glirlt['msg']
                    code = glirlt['code']
            else: uhr +=  f"「{email}」无需重复安置. <br/>"
        else:
            uhr += f"接口访问异常，{ul}"
            stop = 1
            msg = ul['msg']
            code = ul['code']
        if str(isBatch) == "0": stop = 1
        rlt = {"usrlt":uhr,"stop":stop}
        print(f"userSettle-rlt: {rlt}")

    elif action == "userCancelSettle": #取消安置
        cancelDirs = data['cancelDirs']
        prefix, start_num, suffix, num_width = pdef.extract_prefix_and_number(uname)
        if suffix: email = uname
        else: email = uname + emailSuffix
        ul = _get_mif().userlogin(uname,env,version)
        if ul["code"] != 0: return build_response(ul["code"], ul["msg"], ul["msg"])
        uinfo = _get_mif().queryUserInfo(email,env,version)
        userId = uinfo["data"]["user"]["jtUserId"]
        if cancelDirs == "all":
            duhrlt = _get_mif().deleteUpperHierarchy(userId,env,version)
            if duhrlt['code'] == 0:
                rlt += f"用户{email}取消上级"
                code = duhrlt['code']
                msg = duhrlt['msg']
            else:
                rlt += duhrlt['msg']
                code = duhrlt['code']
                msg = duhrlt['msg']
            dlhrlt = _get_mif().deleteLowerHierarchy(userId,env,version)
            if dlhrlt['code'] == 0:
                rlt += f"和下级的安置关系。"
                code = dlhrlt['code']
                msg = dlhrlt['msg']
            else:
                rlt += dlhrlt['msg']
                code = dlhrlt['code']
                msg = dlhrlt['msg']
        elif cancelDirs == "up":
            duhrlt = _get_mif().deleteUpperHierarchy(userId,env,version)
            if duhrlt['code'] == 0:
                rlt += f"用户{email}取消上级安置关系。"
                code = duhrlt['code']
                msg = duhrlt['msg']
            else:
                rlt += duhrlt['msg']
                code = duhrlt['code']
                msg = duhrlt['msg']
        elif cancelDirs == "down":
            dlhrlt = _get_mif().deleteLowerHierarchy(userId,env,version)
            if dlhrlt['code'] == 0:
                rlt += f"用户{email}取消下级安置关系。"
                code = dlhrlt['code']
                msg = dlhrlt['msg']
            else:
                rlt += dlhrlt['msg']
                code = dlhrlt['code']
                msg = dlhrlt['msg']

    elif action == "issettle": #是否安置查询
        prefix, start_num, suffix, num_width = pdef.extract_prefix_and_number(uname)
        if suffix: email = uname
        else: email = uname + emailSuffix
        ul = _get_mif().userlogin(uname,env,version)
        if ul["code"] == 0:
            gtrlt = _get_mif().getTree(env, version)
            pprc = gtrlt['data']['placementParentReferralCode']
            ppemail = gtrlt['data']['placementParentEmail']
            if not pprc:
                rlt = f"用户「{uname}」未被安置。"
            else:
                if ppemail: ppe = f"「{ppemail}」"
                else: ppe = None
                rlt = f"用户「{uname}」安置上级为{ppe}。"
            code = gtrlt["code"]
            msg = gtrlt["msg"]
        else:
            rlt = ul["msg"]
            code = ul["code"]
            msg = ul["msg"]

    elif action=="giftPoints": #赠送点位
        leveldict = {"-1":"尊享","3":"银级","1":"金级","2":"白金","4":"钻石"}
        prefix, start_num, suffix, num_width = pdef.extract_prefix_and_number(uname)
        if suffix: email = uname
        else: email = uname + emailSuffix
        ul = _get_mif().userlogin(uname,env,version)
        if ul["code"] != 0: return build_response(ul["code"], ul["msg"], ul["msg"])
        uinfo = _get_mif().queryUserInfo(email,env,version)
        userId = uinfo["data"]["user"]["jtUserId"]
        level,amount,expire = data["level"],data["amount"],data["expire"]
        saprlt = _get_mif().sendAccountPoint(userId,level,amount,expire,env,version)
        levelname = leveldict.get(level,"") 
        if saprlt["code"] == 0: rlt = f"赠送用户[{email}] {amount} 个{levelname}点位 (有效期 {expire} 天)。"
        else: rlt = msg
        code = saprlt["code"]
        msg = saprlt["msg"]

    elif action == "assetChange": #账户余额充值/扣减
        prefix, start_num, suffix, num_width = pdef.extract_prefix_and_number(uname)
        if suffix: email = uname
        else: email = uname + emailSuffix
        ul = _get_mif().userlogin(uname,env,version)
        if ul["code"] != 0: return build_response(ul["code"], ul["msg"], ul["msg"])
        uinfo = _get_mif().queryUserInfo(email,env,version)
        userId = uinfo["data"]["user"]["jtUserId"]
        camount,state = data["camount"],data["state"]
        amount = int(camount) * 100
        acrlt = _get_mif().assetChange(userId,amount,state,env,version)
        states = {"0":"扣减","1":"充值"}
        if acrlt["code"] == 0: rlt = f'用户"{uname}"{states.get(state,"")}余额「{camount}」元.'
        else: rlt = acrlt["msg"]
        code,msg = acrlt["code"],acrlt["msg"]

    elif action == "getNeedSetInfo":  # 查询待安置人数（admin 接口，用 userId 免登）
        userId = data.get("userId", "")
        if not userId:
            # 首次调用：通过 uname 登录获取 userId
            uname_val = data.get("uname", "")
            if not uname_val:
                rlt = {"needSetCnt": 0, "needSetUserList": [], "rootUserId": ""}
                code = c["success"]
                msg = m["success"]
            else:
                email = uname_val + data.get("emailSuffix", "@jt.com")
                ul = _get_mif().userlogin(uname_val, env, version)
                if ul["code"] == 0:
                    uinfo = _get_mif().queryUserInfo(email, env, version, "(originview-getNeedSetInfo)")
                    userId = uinfo["data"]["user"]["jtUserId"]
                else:
                    return build_response(ul.get("code", -1), ul.get("msg", "登录失败"), ul.get("msg", ""))
        if userId:
            nsi = _get_mif().getNeedSetInfo(userId, env, version)
            if nsi and nsi.get("code") == 0:
                need_data = nsi.get("data", {})
                rlt = {
                    "rootUserId": userId,
                    "needSetCnt": need_data.get("needSetCnt", 0),
                    "needSetUserList": need_data.get("needSetUserList", []),
                }
                code = c["success"]
                msg = m["success"]
            else:
                rlt = nsi.get("msg", "查询失败") if nsi else "查询失败"
                code = nsi.get("code", -1) if nsi else -1
                msg = nsi.get("msg", "") if nsi else ""

    elif action == "getNeedSetLocationInfo":  # 查询可安置位置
        userId = data.get("userId", "")
        nsl = _get_mif().getNeedSetLocationInfo(userId, env, version)
        if nsl and nsl.get("code") == 0:
            rlt = nsl.get("data", [])
            code = c["success"]
            msg = m["success"]
        else:
            rlt = nsl.get("msg", "查询失败") if nsl else "查询失败"
            code = nsl.get("code", -1) if nsl else -1
            msg = nsl.get("msg", "") if nsl else ""

    elif action == "setHierarchy":  # 执行安置
        upperUserId = data.get("upperUserId", "")
        lowerUserId = data.get("lowerUserId", "")
        side = data.get("side", "")
        rootUserId = data.get("rootUserId", "")
        shrlt = _get_mif().setHierarchy(upperUserId, lowerUserId, side, rootUserId, env, version)
        if shrlt and shrlt.get("code") == 0:
            rlt = "安置成功！"
            code = c["success"]
            msg = m["success"]
        else:
            rlt = shrlt.get("msg", "安置失败") if shrlt else "安置失败"
            code = shrlt.get("code", -1) if shrlt else -1
            msg = shrlt.get("msg", "") if shrlt else ""

    elif action == "cancelUpperSettle":  # 移除上级安置关系
        userId = data.get("userId", "")
        duhrlt = _get_mif().deleteUpperHierarchy(userId, env, version)
        if duhrlt and duhrlt.get("code") == 0:
            rlt = "已移除上级安置关系。"
            code = c["success"]
            msg = m["success"]
        else:
            rlt = duhrlt.get("msg", "操作失败") if duhrlt else "操作失败"
            code = duhrlt.get("code", -1) if duhrlt else -1
            msg = duhrlt.get("msg", "") if duhrlt else ""

    elif action == "cancelLowerSettle":  # 移除下级安置关系
        userId = data.get("userId", "")
        dlhrlt = _get_mif().deleteLowerHierarchy(userId, env, version)
        if dlhrlt and dlhrlt.get("code") == 0:
            rlt = "已移除下级安置关系。"
            code = c["success"]
            msg = m["success"]
        else:
            rlt = dlhrlt.get("msg", "操作失败") if dlhrlt else "操作失败"
            code = dlhrlt.get("code", -1) if dlhrlt else -1
            msg = dlhrlt.get("msg", "") if dlhrlt else ""

    elif action == "delAccount":
        accounts = data.get("accounts", [data.get("account", "")])
        pwd = data.get("pwd", "")
        if not accounts:
            rlt = "账号列表为空"
            code, msg = -1, "no data"
        else:
            ok, fail = 0, []
            for acct in accounts:
                ul = _get_mif().userlogin(acct, env, version, pwd)
                if ul.get("code") == 0:
                    drlt = _get_mif().delAccount(env)
                    if drlt.get("code") == 0:
                        ok += 1
                        _del_mmeett_regist(acct, pwd)
                    else:
                        fail.append(f"{acct}: {drlt.get('msg', '未知')}")
                else:
                    fail.append(f"{acct}: 登录失败 - {ul.get('msg', '')}")
            if ok == 1:
                rlt = f"{accounts[0]} 注销成功"
            elif ok > 1:
                rlt = f"{accounts[0]}~{accounts[ok-1]} 注销成功，共 {ok} 个"
            else:
                rlt = ""
            if fail:
                rlt += f" | 失败 {len(fail)} 个 ({'; '.join(fail[:3])})"
            code = c['success'] if ok > 0 else -1

            msg = m['success'] if ok > 0 else "全部注销失败"

    return build_response(code, msg, rlt)

@login_required
@never_cache
def mmeettTreeView(request):
    return redirect('/')

@never_cache
def pmmeettTreeData(request):
    data = json.loads(request.body)
    uname = data.get("uname", "")
    env = data.get("env", "test")
    version = data.get("version", 7)
    deep = data.get("deep", "")
    emailSuffix = data.get("emailSuffix", "@jt.com")
    # 先登录获取token
    prefix, start_num, suffix, num_width = pdef.extract_prefix_and_number(uname)
    if suffix: email = uname
    else: email = uname + emailSuffix
    ul = _get_mif().userlogin(uname,env,version)
    if ul["code"] != 0: return jr({"code": ul["code"], "msg": ul.get("msg", "登录失败"), "data": ""})
    uinfo = _get_mif().queryUserInfo(email,env,version,"(pmmeettTreeData)")
    userId = uinfo["data"]["user"]["jtUserId"]
    tree_rlt = _get_mif().getTree(env, version, userId, deep)
    return jr(tree_rlt)

@never_cache
def pmmeettTreeChildren(request):
    """懒加载指定用户的子节点"""
    data = json.loads(request.body)
    env = data.get("env", "test")
    version = data.get("version", 7)
    userId = data.get("userId", "")
    deep = 5
    tree_rlt = _get_mif().getTree(env, version, userId, deep)
    return jr(tree_rlt)

@login_required
@never_cache
def xcard(request):
    return redirect('/')

@never_cache
def pxcard(request, action):
    data = json.loads(request.body)
    desc = data["desc"]
    env = data["env"]
    uname = data["uname"]
    emailSuffix = data["emailSuffix"]
    bnum = data["bnum"]
    prefix, start_num, suffix, num_width = pdef.extract_prefix_and_number(uname)
    code = c['success']
    msg = m['success']
    rlt = ""

    DBNAME_MAP = {"indo": "xcard", "taiwan": "xcard_tw"}

    def process_user(email):
        gtblrlt = _get_xc().getTokenByLogin(email, desc, env)
        print("userBuyCard-gtblrlt:", gtblrlt)
        if gtblrlt:
            if gtblrlt["code"] != 0:
                return f"用户「{email}」获取token失败，原因{gtblrlt} <br/>"
            qcirlt = _get_xc().queryUserInfo(email, desc, env)
            print("userBuyCard-qcirlt:", qcirlt)
            userId = qcirlt["data"]["userVipInfo"]["userId"]
            msp("xcard", DBNAME_MAP.get(desc, "")).execute(
                "update user_vip_info set valid_amt = 9999900 where user_id = %s;", userId)
            _get_xc().sendMail(email, desc, env)
            _get_xc().setPaymentPassword(email, desc, env)
            country = data.get('country')
            if desc == "taiwan" and country in ('3630979328925976', '3630979328925782'):
                productId = data['productId']
                countryCode = qcirlt['data']['user']['countryCode']
                gcrlt = _get_xc().getCountry(desc, env)
                for ci in gcrlt['data']:
                    if ci['code'] == countryCode:
                        countryName, areaCode = ci['name'], ci['areaCode']
                        break
                addressId = _get_xc().addAddressId(countryCode, countryName, areaCode, desc, env)['data']
                corlt = _get_xc().orderCreate(productId, addressId, desc, env)
                prrlt = _get_xc().paymentRequest(email, corlt['data']['orderId'], desc, env, corlt['data']['orderName'])
                return f"用户「{email}」购买会员{'成功！<br/>' if prrlt['code'] == 0 else '失败，原因: ' + prrlt['msg'] + ' <br/>'}"
            else:
                cardType = data["cardType"]
                mprlt = _get_xc().memberPurchase(email, cardType, desc, env)
                print(f"购买会员结果：{mprlt}")
                if mprlt["code"] == 0:
                    orderId = mprlt["data"]
                    _get_xc().paymentOrder(email, orderId, desc, env)
                    prrlt = _get_xc().paymentRequest(email, orderId, desc, env)
                    return f"用户「{email}」购买会员{'成功！<br/>' if prrlt['code'] == 0 else '失败，原因: ' + prrlt['msg'] + ' <br/>'}"
                else:
                    return f"用户「{email}」获取订单ID失败，原因{mprlt} <br/>"
        else:
            return f"用户「{email}」不存在！<br/>"

    if action == "xcardRegist":
        for i in range(int(bnum)):
            newuname = generate_username(prefix, start_num, i, suffix, num_width)
            if suffix: email = newuname
            else: email = newuname + emailSuffix
            print(f"pxcard-email: {email}, desc: {desc}, env: {env}")
            rsmrlt = _get_xc().rigestSendMail(email, desc, env)
            if rsmrlt["code"] == 0:
                rurlt = _get_xc().registUser(email, data["rcode"], data["country"], desc, env)
                if rurlt["code"] == 0:
                    rlt += f"用户「{email}」注册成功！<br/>"
                else:
                    code = c['reserror']
                    msg = m['reserror']
                    rlt += f"用户「{email}」注册失败，原因：{rurlt} <br/>"
            else:
                code = c['reserror']
                msg = m['reserror']
                rlt += f"用户「{email}」发送验证码失败，原因{rsmrlt} <br/>"

    elif action == "userBuyCard":
        for i in range(int(bnum)):
            newuname = generate_username(prefix, start_num, i, suffix, num_width)
            if suffix: email = newuname
            else: email = newuname + emailSuffix
            rlt += process_user(email)

    elif action == "getCountry":
        rlt = _get_xc().getCountry(desc, env)['data']

    elif action == "addReferralLinks":
        rcode = data["rcode"]
        country = data["country"]
        cardType = data["cardType"]
        for i in range(int(bnum)):
            newuname = generate_username(prefix, start_num, i, suffix, num_width)
            if suffix: email = newuname
            else: email = newuname + emailSuffix
            print(f"before request rigestAndOpenVip: rcode={rcode}, country={country}, cardType={cardType}")
            nrcode, raovrlt = _get_xc().rigestAndOpenVip(i, email, rcode, country, cardType, desc, env)
            rcode = nrcode
            rlt += str(raovrlt)

    return build_response(code, msg, rlt)


@login_required
@never_cache
def soonConfig(request):
    return redirect('/')

@login_required
@never_cache
def setting(request):
    """兼容旧调用方式"""
    if request.method == 'GET':
        return redirect('/')
    data = json.loads(request.body)
    return _process_setting(request, data)

@never_cache
def setting_action(request, action):
    """action 从 URL 路径获取"""
    data = json.loads(request.body)
    data['action'] = action
    return _process_setting(request, data)

def _process_setting(request, data):
    """基线版/soon 企业设置入口：结构化日志 + 异常兜底，方便 Agent 定位问题。"""
    action = data.get('action') or data.get('type', '')
    env = data.get('env', '')
    version = data.get('version', '')
    # 入参脱敏：密码/密钥字段打码，避免明文入库
    _safe = {k: ('***' if k in ('pwd', 'passwd', 'password', 'secret') else v) for k, v in data.items()}
    logger.info(f'[ov/setting] 入参 action={action} env={env} version={version} data={_safe}')
    try:
        result = _process_setting_impl(request, data)
        logger.info(f'[ov/setting] 完成 action={action} env={env} version={version}')
        return result
    except Exception as e:
        # 完整堆栈写入 api.log，Agent 的 read_logs 可直接定位到具体行
        logger.exception(f'[ov/setting] 处理异常 action={action} env={env} version={version} 异常: {e}')
        return build_response(c['reserror'], f"系统异常: {e}", "")


def _process_setting_impl(request, data):
    rlt = ""
    rescode = ""
    msg = ""
    action = data.get('action') or data['type']
    env = data['env']
    version = data.get('version')

    VERSION_CONFIG = {
        3: {'ds': '101', 'addr': {'test': 'https://forigin-test.aijiatui.com/', 'prod': 'https://forigin.aijiatui.com/'}},
        4: {'ds': '108', 'addr': {'test': 'https://soon-admin-dev.aijiatui.com/', 'prod': 'https://soon-admin.aijiatui.com/'}},
        # 5: {'ds': '109', 'addr': {'test': 'https://meet-test-admin.aijiatui.com/', 'prod': 'https://meet-admin.aijiatui.com/'}},
    }

    if action == 'openaccount':
        privaddr = data['privaddr']
        ms = msr[3] if privaddr else msr[1]
        cname = data['cname']
        lname = data['lname']
        pwd = data['pwd']
        ooarlt = _get_ovs().origin_openAccount(cname, data['csname'], data['phone'], lname, pwd, data['langType'], data['etime'], env, data['version'], privaddr)
        if ooarlt['code'] == 0 and ooarlt['data']:
            companyId = ooarlt['data']
            rescode, msg = c['success'], m['success']
            if version == 3:
                config = VERSION_CONFIG[3]
                addr = config['addr'][env]
                mta = data['mta']
                ucrlt = ""
                if mta:
                    oucirlt = _get_ovs().origin_updateCompanyInfo(companyId, mta, "", "", "", "", env, version)
                    if oucirlt['code'] == 0:
                        ucrlt = f" 销售席位数为【{mta}】."
                rlt = f'企业ID: {companyId}{ucrlt}<br/> 后台地址:{addr} 账号: {lname}, 密码: {pwd}. '
                oprlt = f"基线版企业开户成功【{lname}, {pwd}】, 有效期 {data['etime']}！" + ucrlt
            else:
                config = VERSION_CONFIG.get(version, {})
                addr = config['addr'].get(env, '')
                rlt = f'企业ID: {companyId}<br/> 后台地址:{addr} 账号: {lname}, 密码请查收邮件(若对应账号已有密码，则复用该密码)。'
                oprlt = f"{VERSION_MAP.get(version, '')}版企业开户成功【{lname}，密码请查收邮件(如账号已注册且有密码，请复用该密码)】！"
            pu.ov_opretor_records_instdb(companyId, cname, env, request.session.get('uid'), request.session.get('uname'), oprlt, ms, config.get('ds', ''), version)
        else:
            rescode, msg, rlt = c['reserror'], m['reserror'], f'企业开户异常, {ooarlt["msg"]}'

    elif action == "resetpv": #修改SOON版会员
        bpoc = data["bpoc"]
        pv = data["pv"]
        expt = data["expt"]
        env2 = data["env"]
        version2 = data["version"]
        if bpoc == "company":
            compId, cardId, whosv = data["compId"], "", f"企业({data['compId']})为'{PV_VERSION_MAP.get(pv, '')}'版"
        else:
            compId, cardId, whosv = 0, data["cardId"], f"员工({data['cardId']})为'{PV_VERSION_MAP.get(pv, '')}'版"
        ssvrlt = _get_ovs().soon_setVersion(compId, cardId, pv, expt, env2, version2)
        if ssvrlt['code'] == 0:
            rescode, msg = c['success'], m['success']
            rlt = f"设置【{whosv}】成功, 有效期至{expt}！"
            pu.ov_opretor_records_instdb(compId, "", env2, request.session.get('uid'), request.session.get('uname'), rlt, msr[1], 103, version2)
        else:
            rescode, msg, rlt = c['reserror'], m['reserror'], f"设置版本异常, {ssvrlt['msg']}"

    elif action == 'setnfcservice':
        ssnsrlt = _get_ovs().soon_setNfcService(data['cardId'], data['code'], data['env'], version)
        if ssnsrlt['code'] == 0:
            rescode, msg, rlt = c['success'], m['success'], f"名片({data['cardId']})绑定NFC({data['code']})成功！"
        else:
            rescode, msg, rlt = c['reserror'], m['reserror'], f"名片绑定NFC卡片异常！{ssnsrlt['msg']}"

    elif action == "rmvnfcservice":
        srnsrlt = _get_ovs().soon_rmvNfcService(data['code'], data['env'], version)
        if srnsrlt['code'] == 0:
            rescode, msg, rlt = c['success'], m['success'], f"名片解绑NFC({data['code']})成功！"
        else:
            rescode, msg, rlt = c['reserror'], m['reserror'], f"名片解绑NFC卡片异常, {srnsrlt['msg']}"

    elif action == "getflink":
        ftype, fileId, cardId, holderId = data["ftype"], data["fileId"], data["cardId"], data["holderId"]
        soonUri = (_get_ovs().soonTestUri if version == 4 else _get_ovs().meetTestUri) if env == "test" else (_get_ovs().soonProdUri if version == 4 else _get_ovs().meetProdUri)
        FTYPE_MAP = {"dcard": ("0", "/s/"), "file": ("7", "/user/share/file?type=file&shareId="), "video": ("6", "/user/share/file?type=video&shareId="), "product": ("1", "/user/share/file?type=product&shareId="), "case": ("5", "/user/share/file?type=case&shareId=")}
        actionType, m_url = FTYPE_MAP.get(ftype, ("", ""))
        sgejrlt = _get_ovs().soon_getExtensionJson(fileId, actionType, cardId, holderId, env, version)
        extjson = sgejrlt["data"]["extensionJson"]
        shareId = _get_ovs().soon_getShareId(fileId, actionType, cardId, holderId, extjson, env, version)["data"]
        rlt = soonUri + m_url + shareId
        rescode, msg = c['success'], m['success']

    elif action == 'savewxappinfo':
        ms = msr[3] if data['privaddr'] else msr[1]
        owairlt = _get_ovs().origin_saveOrUpdateWxAppInfo(data['cid'], data['appid'], data['secret'], env, 3, data['privaddr'])
        if owairlt['code'] == 0 and owairlt['data']:
            rescode, msg = c['success'], m['success']
            rlt = f'企业（{data["cid"]}）绑定小程序（{data["appid"]}）成功! '
            pu.ov_opretor_records_instdb(data['cid'], "", env, request.session.get('uid'), request.session.get('uname'), rlt, ms, '102', "3")
        else:
            rescode, msg, rlt = c['reserror'], m['reserror'], f'企业绑定小程序异常, {owairlt["msg"]}'

    elif action == "updcompinfo":
        ms = msr[3] if data['privaddr'] else msr[1]
        oucirlt = _get_ovs().origin_updateCompanyInfo(data['compid'], data["mta"], data["cs"], data["aics"], data["isl"], data["expireTime"], env, version, data['privaddr'])
        cinfo = []
        if oucirlt['code'] == 0:
            if data["mta"]:
                cinfo.append(f"员工账号数为【{'无限制' if int(data['mta']) == 0 else data['mta']}】")
            if data["cs"]:
                csn = CS_STATUS_MAP.get(int(data["cs"]), "")
                cinfo.append(f"企业状态为【{csn}】")
            if data["isl"]:
                cinfo.append(f"企业有效期为【{data['expireTime'] if data['expireTime'] else '永久有效'}】")
            if data["aics"]:
                cinfo.append(f"【{'启用' if int(data['aics']) == 1 else '关闭'}】AI名片")
            rescode, msg = c['success'], m['success']
            rlt = f"修改企业信息: {', '.join(cinfo)}！"
            pu.ov_opretor_records_instdb(data['compid'], "", env, request.session.get('uid'), request.session.get('uname'), rlt, ms, 104, version)
        else:
            rescode, msg, rlt = c['reserror'], m['reserror'], f"修改企业信息异常, {oucirlt['msg']}"

    elif action == 'initpwd':
        newpwd = pdef.md5_encryp(data['passwd'], '0')
        oipwd = _get_ovs().origin_initpassword(data['userid'], newpwd, env=env)
        if oipwd['code'] == 0:
            rescode, msg, rlt = c['success'], m['success'], f"用户（{data['userid']}）密码初始化成功！"
        else:
            rescode, msg, rlt = c['reserror'], m['reserror'], f"用户（{data['userid']}）密码初始化失败，原因：{oipwd['msg']}"

    elif action == "getEDByCID":
        gcirlt = _get_ovs().getCompInfoByCompId(data["compId"], env)
        if gcirlt["code"] == 0 and gcirlt["data"]:
            rlt = gcirlt['data']['expireTime'][:10]
            rescode, msg = c['success'], m['success']
        else:
            rescode, msg, rlt = c['reserror'], m['reserror'], f"获取企业信息异常，原因{gcirlt['msg']}"

    elif action == "getuidbyemail":
        sguberlt = _get_ovs().soon_getUidByEmail(data["email"], env, version)
        if sguberlt['code'] == 0:
            rescode, msg, rlt = c['success'], m['success'], sguberlt['data']["id"]
        elif sguberlt['code'] == 43266:
            rescode, msg, rlt = sguberlt['code'], "用户‘邮箱/手机’不存在。", sguberlt["msg"]
        else:
            rescode, msg, rlt = c['reserror'], m['reserror'], sguberlt["msg"]

    elif action == "setnewhome":
        squirlt = _get_ovs().soon_queryUserInfoByUid(data["userId"], env, version)
        userEmail = squirlt.get("data", {}).get("email")
        if not userEmail:
            return jr({"code": 10003, "msg": "用户ID不存在！"})
        ssnhrlt = _get_ovs().soon_setNewHome(data["userId"], data["status"], env, version)
        if ssnhrlt["code"] == 0:
            snm = "大众版" if data["status"] == "0" else "Tommy版"
            rlt, rescode, msg = f"设置用户「{userEmail}」为「{snm}」", c['success'], m['success']
        else:
            rlt, rescode, msg = f"设置用户「{userEmail}」版本失败，{ssnhrlt['msg']}", c['reserror'], m['reserror']

    elif action == "addduration":
        bpoc, ccid = data["bpoc"], data["ccid"]
        companyId, cardId, pr = (0, ccid, f"用户({ccid}): ") if bpoc == "personal" else (ccid, "", f"企业({ccid}): ")
        sadrlt = _get_ovs().soon_addduration(companyId, cardId, data["duration"], data["dtype"], data["etime"], env, version)
        if sadrlt["code"] == 0:
            dt = f"发放类型为「{DURATION_TYPE_MAP.get(data['dtype'], '')}」, " if data["dtype"] else ""
            etrlt = data["etime"] if data["etime"] else "永久有效"
            rlt, rescode, msg = f"{pr}发放 {data['duration']} 分钟, {dt}有效期为「{etrlt}」。", c['success'], m['success']
            pu.ov_opretor_records_instdb(companyId, "", env, request.session.get('uid'), request.session.get('uname'), rlt, msr[1], 107, version)
        else:
            rescode, msg, rlt = c['reserror'], m['reserror'], f"发放工时失败，{sadrlt['msg']}"

    elif action == "removedevice":
        srdrlt = _get_ovs().soon_removeDevice(data["deviceNo"], data["cardId"], env, version)
        cr = f"员工「{data['cardId']}」的" if data["cardId"] else ""
        if srdrlt['code'] == 0:
            rlt, rescode, msg = f"解绑{cr}翻译器【{data['deviceNo']}】成功。", c['success'], m['success']
            pu.ov_opretor_records_instdb("/", "/", env, request.session.get('uid'), request.session.get('uname'), rlt, msr[1], 110, version)
        else:
            rescode, msg, rlt = c['reserror'], m['reserror'], f"解绑翻译器失败，{srdrlt['msg']}"

    elif action == "cryptoEncrypt":  # 加密
        version = data.get("version", 4)
        value = data.get("value", "")
        cr = _get_ovs().cryptoEncrypt(value, env, version)
        if cr and cr.get("code") == 0:
            rlt = cr.get("data", "加密完成")
            rescode, msg = c["success"], m["success"]
        else:
            rlt = cr.get("msg", "加密失败") if cr else "加密失败"
            rescode = cr.get("code", -1) if cr else -1
            msg = cr.get("msg", "") if cr else ""

    elif action == "cryptoDecrypt":  # 解密
        version = data.get("version", 4)
        value = data.get("value", "")
        cr = _get_ovs().cryptoDecrypt(value, env, version)
        if cr and cr.get("code") == 0:
            rlt = cr.get("data", "解密完成")
            rescode, msg = c["success"], m["success"]
        else:
            rlt = cr.get("msg", "解密失败") if cr else "解密失败"
            rescode = cr.get("code", -1) if cr else -1
            msg = cr.get("msg", "") if cr else ""

    return build_response(rescode, msg, rlt)

@login_required
@never_cache
def twCompSet(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        print(' -- [%s] "通威企业设置"' % gct())
        code, msg, rlt = "", "", ""
        data = json.loads(request.body)
        action = data["type"]
        env = data["env"]
        version = data["version"]

        TW_ADDR_MAP = {"test": "https://demon.aijiatui.com/bms/", "prod": "https://ai-card.aijiatui.com/bms/"}

        if action == "twopenaccount":
            templateNo = data["templateNo"]
            mta = data["mta"]
            etime = str(data["etime"]) + " 23:59:59"
            addr = TW_ADDR_MAP.get(env, "")
            twoa = _get_ovs().tw_openAccount(data["cname"], data["csname"], data["aname"], data["lp"], mta, etime, env, version, templateNo)
            if twoa['code'] == 0:
                code, msg = c['success'], m['success']
                rlt = f"通威企业ID: <b>{twoa['data']}</b> (<b>{data['cname']}</b>)<br/> 后台地址: <b>{addr}</b> 账号: <b>{data['lp']}</b>, 密码: <b>a123456</b>。"
                pu.ov_opretor_records_instdb(twoa["data"], data["cname"], env, request.session.get('uid'), request.session.get('uname'), rlt, msr[1], '105', version)
            else:
                code, msg, rlt = c['reserror'], m['reserror'], f"开户失败, {twoa['msg']}"

        elif action == "twbindapplet":
            twba = _get_ovs().tw_bindApplet(data['cid'], data["appid"], data["secret"], env)
            if twba['code'] == 0:
                code, msg = c['success'], m['success']
                rlt = f"通威企业({data['cid']})绑定小程序({data['appid']})成功！"
                pu.ov_opretor_records_instdb(data['cid'], "", env, request.session.get('uid'), request.session.get('uname'), rlt, msr[1], '106', version)
            else:
                code, msg, rlt = c['reserror'], m['reserror'], f"绑定小程序失败, {twba['msg']}"

        elif action == "twsetrecord":
            cid = data["cid"]
            cinfo = []
            if data["mta"]:
                mta = data["mta"]
                cinfo.append(f"销售席位数为【{'无限制' if int(data['mta']) == 0 else data['mta']}】")
            else: mta = ""
            if data["cs"]:
                cs = data["cs"]
                csn = CS_STATUS_MAP.get(int(data["cs"]), "")
                cinfo.append(f"企业状态为【{csn}】")
            else: cs = ""
            if data["etime"]:
                etime = str(data["etime"]) + " 23:59:59"
                cinfo.append(f"企业有效期为【{data['etime']}】")
            else: etime = ""
            ucirlt = _get_ovs().updateTWCompanyInfo(cid,mta,etime,cs,env,version)
            if ucirlt["code"] == 0:
                rlt = f"修改企业信息: {', '.join(cinfo)}！"
                code, msg = c['success'], m['success']
                pu.ov_opretor_records_instdb(data['cid'], "", env, request.session.get('uid'), request.session.get('uname'), rlt, msr[1], 109, version)
            else:
                code, msg, rlt = ucirlt["code"],ucirlt["msg"],ucirlt["msg"]

        return build_response(code, msg, rlt)


def page_404(request, action=None):
    """自定义 404（已禁用的页面）"""
    from django.http import Http404
    raise Http404("页面已禁用")
