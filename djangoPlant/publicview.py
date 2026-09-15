from. import logger,json,current_dir,JsonResponse as jr,re,csrf_exempt,NULL,urlencode,HttpResponse as hr,StreamingHttpResponse,make_password,Colors,redirect,login_required,never_cache,cache_page,cache,ast,time,requests
from django.views.decorators.http import condition
from.pub_InputAndQuery import InputAndQuery
from.publicDef import publicDef,fivemillion
from.compOpenAccount import compOpenAccount
from.ai_xfxh import SparkChatClient, prewarm
from.ai_agent import agent_stream as _agent_stream
import uuid as _uuid
from.cloud_upload import upload_image
from django.contrib.auth.models import User # type: ignore
from.config.codemess import masseges as m, codes as c
from.pub_utils import create_user_with_beijing_time

iaq = InputAndQuery()
pdef = publicDef()
fm = fivemillion()
coa = compOpenAccount()
_scc_instance = None

def _get_scc():
    global _scc_instance
    if _scc_instance is None:
        _scc_instance = SparkChatClient()
    return _scc_instance

cccache = current_dir / 'djangoPlant/configFile/CCCache.json' # 构建配置文件路径
mynote = current_dir / "djangoPlant/configFile/mynote.json"

def gct():
    return pdef.getctime()

@login_required
@never_cache
def shell(request):
    return redirect('/')

@login_required
@never_cache
def home(request):
    return redirect('/')

#查询操作记录页数
@never_cache
def pagecount(request):
    print(' ===== [%s] "查询操作记录页数" ====='%pdef.getctime())
    # 优先 Redis 缓存
    total = cache.get('cccache:orPages')
    if total is None:
        with open(cccache, 'r') as infile:
            fdata = json.load(infile)
        total = ast.literal_eval(fdata["orPages"])
        cache.set('cccache:orPages', total, 3600)
    data = json.loads(request.body)
    env = data['env']
    vers = data['vers']
    compid = data['compid']
    compname = data['compname']
    uname = data['uname']
    minfo = data['minfo']
    try:
        kw = iaq.qm_kw(env,vers,compid,compname,uname,minfo)
        # print('1-kw-count:',kw,'【over】')
        totalrlt = iaq.query_message_total(kw)
        # print(f"total: {totalrlt}")
        total = str(totalrlt["c"])
    except Exception as e:
        total = "0"
    # print(pdef.logcss(gct(),"【publicview-other】pagecount_total:"),total)
    tdata = {"total":total}
    code = c['success']
    msg = m['success']
    rlt = pdef.get_result(code,msg,tdata)
    return jr(rlt)

# 其他
@login_required
@never_cache
# @cache_page(3600)
def other(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        print(' ===== [%s] "其他" ====='%pdef.getctime())
        #获取页面数，设置默认值
        data = json.loads(request.body)
        # print(pdef.logcss(gct(),"【publicview-other】前端调用时传的data:"), data)
        num = data['num']
        env = data['env']
        vers = data['vers']
        page = data['page']
        compid = data['compid']
        compname = data['compname']
        un = data['uname']
        minfo = data['minfo']
        if page == 1: p=0
        else: p = 10 * (int(page)-1)
        # print(pdef.logcss(gct(),"【publicview-other】页数p:"),p)
        kw = iaq.qm_kw(env,vers,compid,compname,un,minfo)
        print(pdef.logcss(gct(),"【publicview-other】查询条件kw:"),kw)
        try:
            query_msgData = iaq.query_message1(num,p,kw)
            # print(f"query_msgData: {query_msgData}")
            get_message1 = {}
            x = 0
            for i in query_msgData:
                if i["q_env"] == 'test': env = '测试'
                elif i["q_env"] == 'prod': env = '生产'
                elif i["q_env"] == 'nxlt': env = '宁夏联通'
                if str(i["update_time"]) == 'None':
                    t = str(i["create_time"])
                else:
                    t = str(i["update_time"])
                get_message1[x] = {"id":i["id"],"env":env,"companyName":i["company_name"],"companyId":str(i["company_id"]),"message":i["message"],"uname":i["uname"],"createTime":t,"serverSide":i["server_side"],"version":i["version"]}
                x += 1
            gm = list(get_message1.values())
        except Exception as e:
            gm = f"数据库连接异常！{e}"
        # print(pdef.logcss(gct(),"【publicview-other】query_message1:"),gm)
        crlt = {"oprationalInfo":gm}
        code = c['success']
        msg = m['success']
        rlt = pdef.get_result(code,msg,crlt)
        return jr(rlt)

@never_cache
def other_part(request, part):
    grlt = ""
    if part == "queryOpraterName":
        try:
            rlt = iaq.query_opraterName()
            for i in rlt:
                grlt += i['uname']+","
            # print(pdef.logcss(gct(),f"【originview-other_part】"),f"queryOpraterName:{grlt}, type: {type(grlt)}")
        except Exception as e:
            # print(pdef.logcss(gct(),"【originview-other_part】queryOpraterName-查询异常，","error"),e)
            grlt = "数据库连接异常！"
    elif part == "delmsg":
        data = json.loads(request.body)
        # print("other_part=>delmsg:",data)
        try:
            id = data["id"]
            rlt = iaq.del_message(id)
            if rlt == 1:
                grlt = "删除成功！"
        except Exception as e:
            # print(pdef.logcss(gct(),"【originview-other_part】delmsg-查询异常，","error"),e)
            grlt = "数据库连接异常！"
    rdata = {"otherPartRlt":grlt}
    code = c['success']
    msg = m['success']
    rlt = pdef.get_result(code,msg,rdata)
    return jr(rlt)

# 我的记录
@login_required
@never_cache
def gmynote(request):
    return redirect('/')

@never_cache
def pmynote(request,opration):
    print(' ===== [%s] "我的记录" ====='%pdef.getctime())
    if True:
        data = json.loads(request.body)
        try:
            with open(mynote, 'r') as infile:
                mdata = json.load(infile)
        except Exception as e:
            return jr(pdef.get_result(c["nojson"],m['nojson'],e))
        if opration == 'istnote':
            tit = data['tit']
            nc = data['nc']
            ct = pdef.getctime()
            ut = ""
            user = request.session.get('uname')
            status = 0
            if len(mdata)>0:
                id = mdata[-1]['id'] + 1
            else:
                id = 1
            # print("id:",id)
            mnote = {"id":id,"tit":str(tit),"nc":str(nc),"user":user,"ct":ct,"ut":ut,"status":status}
            mdata.append(mnote)
            with open(mynote, 'w') as f:
                json.dump(mdata, f, ensure_ascii=False)
            code = c['success']
            msg = m['success']
            rdata = "数据插入成功! "
        elif opration == "getnote":
            param = data["param"]
            if len(mdata) == 0:
                code = c['nodata']
                msg = m['nodata']
                rdata = ""
            else:
                if param == 0:
                    mdrlt = [qd for qd in mdata if qd['status']==0]
                else:
                    mdrlt = [qd for qd in mdata if (param in qd['tit'] or param in qd['nc']) and qd['status']==0]
                if len(mdrlt) == 0:
                    code = c['nodata']
                    msg = m['nodata']
                    rdata = ""
                else:
                    #按最新更新
                    sorted_data = sorted(mdrlt, key=pdef.get_sorting_key, reverse=True)
                    code = c['success']
                    msg = m['success']
                    rdata = sorted_data
        elif opration == "editnote":
            nid = data['id']
            newtit = data['newtit']
            newnc = data['newnc']
            updated_data = {"id":nid,"tit":newtit,"nc":newnc,"ut":pdef.getctime()}
            # 遍历JSON数据并修改
            for item in mdata:
                # print('匹配id：',item['id'],nid)
                if item['id'] == nid:
                    item.update(updated_data)
            # print('修改后的data：',mdata)
            with open(mynote, 'w') as f:
                json.dump(mdata, f, ensure_ascii=False)
            code = c['success']
            msg = m['success']
            rdata = "修改成功!"
        elif opration == 'delnote':
            with open(mynote, 'r') as infile:
                mdata = json.load(infile)
            id_to_remove = int(data['id'])
            afterdel_data = {"status": 1}
            for item in mdata:
                if item['id'] == id_to_remove:
                    item.update(afterdel_data)
            with open(mynote, 'w') as f:
                json.dump(mdata, f, ensure_ascii=False)
            code = c['success']
            msg = m['success']
            rdata = "删除成功!"
        rlt = pdef.get_result(code,msg,rdata)
    return jr(rlt)

# 用户中心
@login_required
@never_cache
def gusercenter(request):
    return redirect('/')
@never_cache
def usercenter(request,uctype):
    print(' ===== [%s] "用户中心" ====='%pdef.getctime())
    data = json.loads(request.body)
    # print(pdef.logcss(gct(),f"【pulicview-usercenter-data"),f"{data}")
    uctype = data['uctype']
    code = c['success']
    msg = m['success']
    if uctype == "gettotal":
        # SQLite COUNT（有索引，毫秒级）
        lt = cache.get('fmhis:ssq_count')
        if lt is None:
            lt = fm._lottery_count('ssq')
            cache.set('fmhis:ssq_count', lt, timeout=None)
        rlt = {"getTotal": lt}
    elif uctype == 'enc': #md5加密
        txt = data['txt']
        jxuid = data['jxuid']
        # print('加密000: ',txt,"; ",jxuid)
        if jxuid:
            r = pdef.md5_encryp(txt,jxuid)
        else:
            r = pdef.md5_encryp(txt)
        rlt = {"encryption": r}
    elif uctype == 'fm': #获取号码
        nt = int(data['nt'])
        cp = data['cp']
        isl = data['isl'] #是否获取本地
        if cp == 'ssq':
            if isl == 'no':
                rlt = fm.saveSSQ(nt)
            elif isl == 'yes':
                rlt = fm.saveSSQ(nt, isl='yes')
        elif cp == 'dlt':
            rlt = fm.DLT(nt)
        elif cp == 'kl8':
            rlt = fm.happy8(10, nt)

        # 大批量时只返回摘要（避免几 MB 数据卡死页面）
        max_display = 200
        if len(rlt) > max_display:
            summary = f"<div style='font-size:15px;color:#4f6ef7;margin-bottom:8px;'>已生成 {len(rlt)} 条数据（仅展示前 {max_display} 条）</div>"
            rlt = rlt[:max_display]

        if isinstance(rlt[0], tuple):
            # isl='yes' 返回 [(num, count), ...] 格式
            r = str(rlt)
        else:
            r = str(rlt)
        r = r[1:-1]
        r = r.replace("',", "'、")
        r = r.replace("'", "")
        r = r.replace('",', ' /')
        r = r.replace('"', '')
        r = r.replace('(', '')
        r = r.replace(')', '')

        if len(rlt) > max_display:
            r = summary + r
        rlt = {"fiveMillion": r}
    elif uctype == 'coa': #saas企业开户
        cname = data['companyName']
        ctype = data['companyType']
        etime = data['expireTime']
        lname = data['loginName']
        pwd = data['password']
        env = data['env']
        coaccount = coa.comp_openAccount(cname,ctype,etime,lname,pwd,env)
        if coaccount['code'] == 0 and coaccount['msg'] == '成功':
            a = '新企业开户成功！企业信息如下: '
            b = cname + ' / ' + lname + ' / ' + coaccount['data']
        else:
            a = coaccount['msg']
            b = ''
        rlt = {"coaTitle":a,"coaInfo":b}
    elif uctype == 'cld': #清理本地生成的数据
        total = fm._lottery_count('ssq')
        if total == 0:
            crlt = '无数据，无需处理！'
        else:
            fm._lottery_clear_all('ssq')
            crlt = '清理成功！'
        rlt = {"cleanLocalData": crlt}
    elif uctype == "gdt":
        rlt = pdef.getctime()
    elif uctype == "queryuinfo":
        uid = request.session.get("uid", 0)
        job = iaq.query_user_job(uid)
        rlt = {"job": job}
    gr = pdef.get_result(code,msg,rlt)
    return jr(gr)

@never_cache
def registTP(request):
    # 管理员校验：用户管理操作（注册/改角色/删用户）仅 mr==99 可调用，顺带堵住未登录越权
    if request.session.get('mr') != 99:
        gdata = {"registTestPlant": "无权限：仅管理员可执行此操作"}
        return jr(pdef.get_result(c['reserror'], m['reserror'], gdata))
    data = json.loads(request.body)
    name = data['name']
    lname = data['lname']
    email = data['email']
    pwd = data['pwd']
    plant = data['plant']
    urole = int(data['ur'])
    oprate = data['oprate']
    newpwd = pdef.md5_encryp(pwd)
    ln = lname
    if not name:
        name = lname
    # print('ln: ',ln)
    quid = iaq.query_count(ln)
    # print('quid: ',quid)
    if urole == 2: 
        urn = "普通角色"
        isStaff = False
    elif urole == 99: 
        urn = "管理员"
        isStaff = True
    if plant == "tp": isActive = True
    elif plant == "asp": isActive = False
    if oprate == "registUser":
        if quid["c"] == 1: #前几位一致的登录名存在
            a = '登录账号[%s]已存在！'%ln
        else:
            user = create_user_with_beijing_time(ln,name,email,pwd,isActive,isStaff)
            uuid = user.id
            # print('sqlite user data: uuid=%s, ln=%s, name=%s, newpwd=%s, urole=%s, plant=%s'%(uuid,ln,name,newpwd,urole,plant))
            isut = iaq.inst_usertest(uuid,str(ln),str(name),str(newpwd),str(urole))
            # 同步写角色表（双写 menu_role 兜底）
            iaq.set_user_role(uuid, urole)
            a = f'注册成功！id: {isut}'
    else:
        rlt = ""
        try:
            ubn = iaq.query_uuidbyname(ln)
            user = User.objects.get(id=ubn["uuid"])
        except User.DoesNotExist:
            gdata = {"registTestPlant":f"用户 '{ln}' 不存在"}
            code = c['nodata']
            msg = m['nodata']
            rlt = pdef.get_result(code,msg,gdata)
            return jr(rlt)
        if oprate == "modifyRole":
            if ln == request.session.get("ln"):
                # 修改的是当前登录用户自己 → 标记 is_self 给前端处理
                rlt += "【isPwdChanged】"
            if pwd:
                user.set_password(pwd)
                rlt += f"密码修改为 [{pwd}]. "
            if urole:
                if user.is_staff != isStaff:
                    user.is_staff = isStaff
                    rlt += f"角色修改为 [{urn}]. "
                # 同步写角色表（双写 menu_role 兜底）
                iaq.set_user_role(ubn["uuid"], urole)
            if email:
                user.email = email
                rlt += f"邮箱修改为 [{email}]. "
            user.save()
        if oprate == "deleteUser":
            user.is_active = 0
            user.save()
            uduinfo = iaq.delete_user(str(ln))
            rlt = f"删除用户{ln}成功！"
            if uduinfo == 1:
                a = f"用户{ln}的{rlt}"
            else:
                a = str(uduinfo)
    gdata = {"registTestPlant":a}
    code = c['success']
    msg = m['success']
    rlt = pdef.get_result(code,msg,gdata)
    return jr(rlt)

@login_required
@never_cache
def easyIC(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        data = json.loads(request.body)
        uid = request.session.get('uid')
        dtype = data['type']
        if dtype == "gethistory":
            hislist = iaq.query_reqhis(uid)
            j = 0
            hisrlt = {}
            #id,method,host,url,header,param [(1, 'post', 'soonTest', '/user/other/personageWeekBriefSummaryHandel', None, 'NULL')]
            for i in hislist:
                host = i["host"]
                hisrlt[j] = {"method":i["method"],"host":host,"uri":i["url"],"header":i["header"],"param":i["param"],"id":i["id"]}
                j += 1
            print("hisrlt:",hisrlt)
            rlt = hisrlt
        elif dtype == "requestinterface":
            data = json.loads(request.body)
            setreqtype = data["setreqtype"]
            setenv = data["setenv"]
            uri = data["uri"]
            headers = data["headers"]
            # print("easyic-headers:",headers)
            params = data["params"]
            rlt = {}
            if not headers: header = ""
            else: header = json.dumps(headers)
            if not params: param = ""
            elif type(params) == list or type(params) == dict:
                param = params
            else: param = json.loads(params)
            print("easyic-params:",param,type(param))
            if isinstance(param,list):
                j = 0
                for i in param:
                    if setreqtype == "post":
                        # print("000000000000000getRequest-newparam",i)
                        try:
                            prrlt = pdef.postRequest(setenv,uri,headers,i)
                            rbody = prrlt.json()
                            resheader = json.dumps(dict(prrlt.headers))
                        except Exception as e:
                            rbody =  f"<span style='color:red;'><b>接口调用失败，请确认一下环境是否可用!</b></span>"
                            resheader = ""
                        i = json.dumps(i)
                        rlt[j] = {"request_type":setreqtype,"host_uri":setenv+uri,"request_headers":header,"request_params":i,"response_headers":resheader,"response_body":rbody}
                    elif setreqtype == "get":
                        # print("11111111111111getRequest-i:",i)
                        # 将字典转换为 GET 请求的参数部分
                        newp = urlencode(i)
                        # print("11111111111111getRequest-newp:",newp)
                        try:
                            grrlt = pdef.getRequest(setenv,uri,headers,newp)
                            rbody = grrlt.json()
                            resheader = json.dumps(dict(grrlt.headers))
                        except Exception as e:
                            rbody =  f"<span style='color:red;'><b>接口调用失败，请确认一下环境是否可用!</b></span>"
                            resheader = ""
                        rlt[j] = {"request_type":setreqtype,"host_uri":setenv+uri+"?"+newp,"request_headers":header,"response_headers":resheader,"response_body":rbody}
                    j += 1
                print("批量调用接口：",rlt)
            else:
                if setreqtype == "post":
                    prrlt = pdef.postRequest(setenv,uri,headers,params)
                    resheader = json.dumps(dict(prrlt.headers))
                    rlt["0"] = {"request_type":setreqtype,"host_uri":setenv+uri,"request_headers":header,"request_params":params,"response_headers":resheader,"response_body":prrlt.json()}
                elif setreqtype == "get":
                    grrlt = pdef.getRequest(setenv,uri,headers,params)
                    resheader = json.dumps(dict(grrlt.headers))
                print("非批量调用接口：",rlt)
            if not header: header = ""
            if not params: params = ""
            gethis = iaq.query_urlInReqhis(uid,setenv,uri)
            print(f"easyIC-gethis: {gethis}")
            #id,method,host,url,header,param
            if gethis:
                id = gethis["id"]
                iaq.update_reqhis(id, header, params)
            else:
                iaq.inst_reqhis(int(uid),setreqtype,setenv,uri,str(header),str(params))
        code = c['success']
        msg = m['success']
        gr = pdef.get_result(code,msg,rlt)
        return jr(gr)

@login_required
@never_cache
def aitools(request):
    return redirect('/')
@login_required
@never_cache
@condition(etag_func=None)
@csrf_exempt
def aitools_stream(request):
    """流式 SSE 返回 AI 回答 | POST {prompt, id, image?}  image 为可选 base64 字符串"""
    data = json.loads(request.body)
    prompt = data.get("prompt", "")
    chat_id = data.get("id") or 0
    uid = request.session.get("uid", 0)
    session_id = f"u{uid}"
    image_data = data.get("image")  # 前端传来的：base64 数据 或 云端 URL
    cloud_image_url = ""  # 云上传后的 URL（仅当 image_data 是 base64 时会上传）
    image_storage = ""    # 最终存进 DB 的图片引用
    full_text = []

    # ── prompt 合法性检查 ──
    if len(prompt) > 10000 or '{%' in prompt or '{{' in prompt or '<script' in prompt.lower():
        def _reject():
            yield f"data: {json.dumps({'type':'error','content':'请求异常，请刷新页面后重试'})}\n\n"
        return StreamingHttpResponse(_reject(), content_type="text/event-stream")

    # 判断 image_data 是 URL 还是 base64
    is_image_url = image_data and (image_data.startswith("http://") or image_data.startswith("https://"))
    is_image_base64 = image_data and not is_image_url

    def event_stream():
        nonlocal chat_id, full_text, cloud_image_url, image_storage

        # 新对话时清除该用户的内存历史，避免旧对话污染新对话
        if int(chat_id) == 0:
            scc = _get_scc()
            scc._histories.pop(session_id, None)

        yield f"data: {json.dumps({'type':'start'})}\n\n"

        # ── 图片存储（不阻塞，异步云上传）──
        import threading

        if is_image_url:
            image_storage = image_data
        elif is_image_base64:
            image_storage = f"data:image/jpeg;base64,{image_data}"
            def _upload_bg():
                nonlocal cloud_image_url, image_storage
                try:
                    import base64
                    img_bytes = base64.b64decode(image_data)
                    url = upload_image(img_bytes, f"chat_{chat_id}_{int(time.time())}.png")
                    if url:
                        cloud_image_url = url
                        image_storage = url
                except Exception:
                    pass
            threading.Thread(target=_upload_bg, daemon=True).start()

        img_for_llm = image_data if is_image_base64 else (cloud_image_url or image_data)

        # ── LLM 流式调用 ──
        try:
            for evt_type, content in _get_scc().ask_stream(prompt, session_id=session_id, image=img_for_llm):
                if evt_type == "text":
                    full_text.append(content)
                    yield f"data: {json.dumps({'type':'text','content':content})}\n\n"
                elif evt_type == "error":
                    yield f"data: {json.dumps({'type':'error','content':content})}\n\n"
                    return
                elif evt_type in ("status", "search_result", "thinking"):
                    yield f"data: {json.dumps({'type':evt_type,'content':content})}\n\n"
                elif evt_type == "done":
                    break
        except Exception as e:
            print(f"[aitools_stream] 生成异常: {e}")
            yield f"data: {json.dumps({'type':'error','content':f'服务异常：{e}'})}\n\n"
            return

        text_str = "".join(full_text)
        rlt = {"ask": prompt, "answer": text_str}
        if image_storage:
            rlt["image"] = image_storage
        try:
            if int(chat_id) == 0:
                chat_id = iaq.inst_aiText(uid, prompt, json.dumps([rlt], ensure_ascii=False))
            else:
                for h in (iaq.query_aiText(user_id=uid) or []):
                    if h["id"] == int(chat_id):
                        old = h.get("content", "[]")
                        if isinstance(old, str):
                            try: old = json.loads(old)
                            except: old = json.loads(old.replace("'",'"'))
                        if not isinstance(old, list): old = []
                        old.append(rlt)
                        iaq.update_aiText_content(chat_id, json.dumps(old, ensure_ascii=False))
                        break
        except Exception as e:
            print(f"[aitools_stream] 保存失败: {e}")

        yield f"data: {json.dumps({'type':'done','id':chat_id})}\n\n"

    resp = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    resp["Content-Encoding"] = "identity"  # 通知 GZipMiddleware 跳过压缩
    resp["Cache-Control"] = "no-cache, no-transform"
    resp["X-Accel-Buffering"] = "no"
    return resp


@login_required
@never_cache
def agent(request):
    return redirect('/')


@never_cache
def agent_float(request):
    """悬浮 Agent 面板（已迁移至 Vue SPA）"""
    return redirect('/')


@login_required
@never_cache
@condition(etag_func=None)
@csrf_exempt
def agent_stream(request):
    """流式 SSE 返回 ReAct Agent 回答 | POST {input, id}  id 为会话ID（0=新会话）"""
    data = json.loads(request.body)
    user_input = data.get("input", "")
    chat_id = data.get("id") or 0
    uid = request.session.get("uid", 0)

    # ── prompt 合法性检查 ──
    if len(user_input) > 10000 or '{%' in user_input or '{{' in user_input or '<script' in user_input.lower():
        def _reject():
            yield f"data: {json.dumps({'type':'error','content':'请求异常，请刷新页面后重试'})}\n\n"
        return StreamingHttpResponse(_reject(), content_type="text/event-stream")

    def event_stream():
        nonlocal chat_id
        full_text = []
        req_id = _uuid.uuid4().hex[:12]
        logger.info("[agent_stream] req=%s uid=%s chat_id=%s 提问: %s", req_id, uid, chat_id, user_input[:80])

        # 注入当前登录用户上下文（uid/uname），供 mmeett 汇总按登录用户筛选
        user_context = ""
        uname = request.session.get("uname", "")
        if uid:
            user_context = f"当前登录用户：userId={uid}" + (f"，用户名={uname}" if uname else "")

        # ── 多轮上下文：加载当前会话最近 6 轮历史喂回给 LLM ──
        history = []
        if int(chat_id) != 0:
            for h in (iaq.query_agent_chat(user_id=uid) or []):
                if h["id"] == int(chat_id):
                    content = h.get("content", "[]")
                    if isinstance(content, str):
                        try:
                            content = json.loads(content)
                        except Exception:
                            try:
                                content = json.loads(content.replace("'", '"'))
                            except Exception:
                                content = []
                    if isinstance(content, list):
                        history = content[-6:]  # 保留最近 6 轮
                    break

        yield f"data: {json.dumps({'type':'start'})}\n\n"
        for evt_type, content in _agent_stream(user_input, user_context=user_context, history=history, request_id=req_id):
            if evt_type == "text":
                full_text.append(content)
                yield f"data: {json.dumps({'type':'text','content':content})}\n\n"
            elif evt_type == "error":
                yield f"data: {json.dumps({'type':'error','content':content})}\n\n"
                return
            elif evt_type == "status":
                yield f"data: {json.dumps({'type':'status','content':content})}\n\n"
            elif evt_type == "log":
                yield f"data: {json.dumps({'type':'log','content':content})}\n\n"
            elif evt_type == "done":
                break

        # ── 落库（复用 aitools 的多会话模式，但存独立的 agent_chat 表）──
        answer = "".join(full_text)
        rlt = {"ask": user_input, "answer": answer}
        try:
            if int(chat_id) == 0:
                chat_id = iaq.inst_agent_chat(uid, user_input, json.dumps([rlt], ensure_ascii=False))
            else:
                for h in (iaq.query_agent_chat(user_id=uid) or []):
                    if h["id"] == int(chat_id):
                        old = h.get("content", "[]")
                        if isinstance(old, str):
                            try: old = json.loads(old)
                            except: old = json.loads(old.replace("'", '"'))
                        if not isinstance(old, list): old = []
                        old.append(rlt)
                        iaq.update_agent_chat_content(chat_id, json.dumps(old, ensure_ascii=False))
                        break
        except Exception as e:
            print(f"[agent_stream] 保存失败: {e}")

        logger.info("[agent_stream] req=%s uid=%s chat_id=%s 落库完成 answer_len=%d", req_id, uid, chat_id, len(answer))
        yield f"data: {json.dumps({'type':'done','id':chat_id})}\n\n"

    resp = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    resp["Content-Encoding"] = "identity"  # 通知 GZipMiddleware 跳过压缩
    resp["Cache-Control"] = "no-cache, no-transform"
    resp["X-Accel-Buffering"] = "no"
    return resp


@login_required
@never_cache
@condition(etag_func=None)
@csrf_exempt
def agent_history(request):
    """Agent 历史：POST {type, id?}  type=gethishh 查列表 / delhistory 删除"""
    data = json.loads(request.body)
    uid = request.session.get("uid", 0)
    ptype = data.get("type", "")
    if ptype == "gethishh":
        rlt = iaq.query_agent_chat(user_id=uid) or []
        rescode, msg = c['success'], m['success']
    elif ptype == "delhistory":
        did = data.get("id")
        try:
            iaq.del_agent_chat(did)
            rescode, msg, rlt = c['success'], m['success'], "删除成功"
        except Exception as e:
            rescode, msg, rlt = c['reserror'], m['reserror'], f"删除失败: {e}"
    else:
        rescode, msg, rlt = c['dataerr'], m['dataerr'], ""
    return jr(pdef.get_result(rescode, msg, rlt))


@never_cache
def paitools(request,ptype):
    data = json.loads(request.body)
    ptype = data["type"]
    rescode,msg = "",""
    if ptype == "gethishh":
        uid = request.session.get("uid", 0)
        hn = 0
        rlt = {}
        ati = iaq.query_aiText(user_id=uid)
        for i in (ati or []):
            content = i.get("content", "")
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except (json.JSONDecodeError, ValueError):
                    try:
                        content = json.loads(content.replace("'", '"'))
                    except (json.JSONDecodeError, ValueError):
                        content = []
            rlt[hn] = {"id": i["id"], "title": i.get("title", ""), "content": content}
            hn += 1
        rescode = c['success']
        msg = m['success']
    elif ptype == "delhistory":
        did = data.get("id")
        try:
            iaq.del_aiText(did)
            rescode, msg, rlt = c['success'], m['success'], "删除成功"
        except Exception as e:
            rescode, msg, rlt = c['reserror'], m['reserror'], f"删除失败: {e}"
    grlt = pdef.get_result(rescode,msg,rlt)
    return jr(grlt)


# ==================== SAAS企业雷达数据 ====================
RADAR_HOST = "https://agent.aijiatui.com"

@never_cache
def radar_data(request):
    """代理查询雷达数据"""
    company_id = request.GET.get('company_id', '')
    start_time = request.GET.get('start_time', '')
    end_time = request.GET.get('end_time', '')
    page = request.GET.get('page', '1')
    limit = request.GET.get('limit', '100')
    params = {
        'company_id': company_id,
        'start_time': start_time,
        'end_time': end_time,
        'page': page,
        'limit': limit,
    }
    try:
        resp = requests.get(f"{RADAR_HOST}/radar/prod/data", params=params, timeout=30)
        return jr(resp.json())
    except Exception as e:
        return jr({'code': 1, 'msg': f'请求失败: {e}', 'data': [], 'count': 0})


@never_cache
def radar_company(request):
    """根据企业名称搜索企业ID"""
    company_name = request.GET.get('company_name', '')
    try:
        resp = requests.get(f"{RADAR_HOST}/radar/prod/company", params={'company_name': company_name}, timeout=30)
        return jr({'code': 0, 'msg': '成功', 'data': resp.json()})
    except Exception as e:
        return jr({'code': 1, 'msg': f'请求失败: {e}', 'data': []})
