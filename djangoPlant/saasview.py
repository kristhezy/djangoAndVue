from. import logger,json,render,JsonResponse as jr,HttpResponse,NULL,current_dir,datetime,io,os,settings,redirect,login_required,never_cache,cache,ast
from PIL import Image  # type: ignore
from.upgrade_referral import UpgradeReferral
from.QueryInterface import QueryInterface
from.compOpenAccount import compOpenAccount
from.jtKnowledge import jtKnowledge
from.forWeCom import forWeCom
from.pub_InputAndQuery import InputAndQuery
from.get_code import GetCode
from.dzFunction import dzFunction,pdef
from.query_everything import queryEverything
from.ov_setting import OVSetting
from.miniprogram import miniProgram
from. import pub_utils as pu
from.config.codemess import masseges as m, codes as c

shd = pdef.split_hh_dh
ur = UpgradeReferral()
qi = QueryInterface()
coa = compOpenAccount()
jtk = jtKnowledge()
fwc = forWeCom()
iaq = InputAndQuery()
gc = GetCode()
dzf = dzFunction()
qe = queryEverything()
ovs = OVSetting()
mp = miniProgram()

module_keys = ('M100','M103','M104','M105','M107','M108','M109','M110','M111','M112','M113','M114','M119','M120','M127','M128','M129','M131','M132')
company_type = 7
payment = 3
thirdparty_id = 1
msr = [' msr&eureka: 华为云 ','2']

cccache = current_dir / 'djangoPlant/configFile/CCCache.json' # 构建配置文件路径

def gct():
    return pdef.getctime()

# 升级转介绍3.0
@login_required  #登录成功后才能访问的装饰器
@never_cache  #清除页面缓存的装饰器
def upgradeR3(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        print(' -- [%s] "升级转介绍3.0"'%pdef.getctime())
        if True:
            data = json.loads(request.body)
            companyIds = data['companyIds']
            seats = data['seats']
            env = data['env']
            result = {}
            for companyId,seat in zip(shd(companyIds),shd(seats)):
                modules = []
                kw_ct = {'company_type':7}
                kw_sa = {'seat_account':seat}
                kw_rn = {'radar_num':seat}
                ct = {"code":0} #测试环境清除app登录token，这里写死
                rlt1 = ur.update_companyInfo(companyId, env, **kw_ct) # 修改企业类型为7
                if rlt1['code'] == 0:
                    rlt_updateCompType = "修改‘企业类型=%s’、" %kw_ct['company_type']
                else:
                    rlt_updateCompType = "修改企业信息%s失败, %s!" %(kw_ct,rlt1)
                rlt2 = ur.update_company_payment(companyId, payment, env)  # 修改企业付款方式为'预充值'
                if rlt2['code'] == 0:
                    rlt_payment = "‘预充值’、"
                else:
                    rlt_payment = "修改企业打款方式失败, %s!" %rlt2
                rlt5 = ur.update_company_thirdparty(companyId,thirdparty_id,env)  # 修改企业第三方资源方id
                if rlt5['code'] == 0:
                    rlt_updateThirdparty = "‘人资方id=1’、"
                else:
                    rlt_updateThirdparty = "修改企业第三方人力资源方id失败, %s!" %rlt5
                print(pdef.logcss(gct(),f'【saasview-upgradeR3】'),f"{rlt_updateThirdparty}")
                ur.update_companyInfo(companyId, env, **kw_rn) #设置企业雷达总数与企业总席位一致
                rlt3 = ur.update_companyInfo(companyId, env, **kw_sa)  # 更新企业总席位数
                if rlt3['code'] == 0:
                    rlt_updateCompSeat = "‘席位总数=%s’成功! " %kw_sa['seat_account']
                else:
                    rlt_updateCompSeat = "修改企业信息%s失败了!" %kw_sa
                for get_module_key in module_keys:
                    rlt4 = ur.add_company_module(companyId, get_module_key, env)  # 开启企业的转介绍模块
                    if rlt4['code'] == 0:
                        if get_module_key == 'M120':
                            ur.save_coupon_config(companyId,env) #调用保存新优惠券配置信息接口
                        temp_list = pdef.mkToName(get_module_key)
                        modules.append(temp_list)
                        xl = ','.join(modules)
                        rlt_addCompModule = "  添加模块 ‘%s’ 成功! " % xl
                        # print(pdef.logcss(gct(),f'【saasview-upgradeR3】'),f"查询模块接口中存在 {modules} 模块!")
                    else:
                        temp_list = pdef.mkToName(get_module_key)
                        modules.append(temp_list)
                        rlt_addCompModule = "  % s 模块增加失败, %s!" % (modules,rlt4)
                print(pdef.logcss(gct(),f'【saasview-upgradeR3】'),f"{rlt_addCompModule}")
                delmk = 'M115'
                rlt8 = ur.del_company_module(companyId,delmk,env) #删除直播模块
                if rlt8['code'] == 0:
                    rlt_delCompModule = '删除‘直播’成功！'
                else:
                    rlt_delCompModule = '删除‘直播’失败！'
                compInfo = qi.query_companyInfo(companyId, env) #企业信息查询
                if compInfo['data']['companyType'] == 0:
                    rlt_migrateData = ur.migrate_data(companyId, env) # 基础版数据迁移至转介绍3.0
                    if env == 'test':
                        ct = ur.clean_appLoginToken(companyId, env) #清除app登录token
                    else:
                        ct = {"code":0}
                else:
                    rlt_migrateData = ""
                rlt_upgrade = rlt_updateCompType+rlt_payment+rlt_updateCompSeat+rlt_delCompModule+"转介绍3.0企业开通成功! " #将所有结果汇总
                if compInfo['code'] == 0 and ct['code'] == 0:
                    companyName = compInfo['data']['companyName']
                else:
                    companyName = '未知企业'
                ds = 1
                pu.sv_opretor_records_instdb(companyId,env,request.session.get('uid'),request.session.get('uname'),rlt_upgrade,ds,msr[1]) #将结果插入数据库中
                result[companyId]='【'+companyName+'】'+ rlt_upgrade
            a = str(result)
            a = a.replace('", ','"\n') #将','换成'换行'
            a = a.replace("', ","'\n")
            # a = a[1:-1]
            cids = str(companyIds)
            cids = cids[1:-1]
            b = '''REPLACE INTO t_resource_role ( company_id, role_id, resource_id ) 
            SELECT a.company_id, a.role_id, b.resource_id FROM t_role a, t_resource b, ai_company c 
            WHERE a.company_id = c.company_id  AND c.company_id in (%s) AND a.role_type = 0 AND b.resource_id IN 
            (322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,
            353,354,355,356,357,358,359,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,385,
            386,387,388,389,390,391,392,393,394,395,396,397,398,399,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,433,434,435,436);
            <br/>REPLACE INTO t_company_module ( company_id, module_key, switch_status ) SELECT c.company_id, m.module_key, m.switch_status 
            FROM t_module m, ai_company c WHERE c.company_id in (%s) AND m.module_key in ('M129', 'M131', 'M132');''' %(cids,cids) #老企业升级转介绍3.0可能缺失菜单，需要执行sql添加
            if ct['code'] != 0:
                a = "清除app登录token数据接口调用失败%s" %ct
                b = ""
            l = {"upgradeR3":a,"ur3sql":b}
            code = c['success']
            msg = m['success']
            rlt = pdef.get_result(code,msg,l)
        return jr(rlt)

#基础版企业配置
@login_required
@never_cache
def basicCompCfg(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        print(' -- [%s] "基础版企业配置"'%pdef.getctime())
        if True:
            data = json.loads(request.body)
            companyIds = data['companyId']
            mk = data['mk']
            env = data['env']
            l = {}
            mk = [x for x in shd(mk) if x]
            allmk = ["M100","M103","M104","M114","M115","M119","M120","M124"]
            for companyId in shd(companyIds):
                #开通基础物料模块
                addmk = ["M105","M107","M108","M109","M110","M111","M112","M113"]
                for amk in addmk:
                    ur.add_company_module(companyId,amk,env)
                #关闭私域流量模块
                delmk = ["M127","M129","M131","M132","M128","M136","M137","M138"]
                for dmk in delmk:
                    ur.del_company_module(companyId,dmk,env)
                #校验
                ci = qi.query_companyInfo(companyId,env)
                if ci['data']:
                    if int(ci['data']['companyType']) == 7:
                        kw = {"company_type":0}
                        ur.update_companyInfo(companyId,env,**kw)
                else:
                    return "未查询到企业，请确认环境是否正确！"
                a=[]
                b=[] #必须放在循环内，每次循环时，才能清空之前的数据
                rlt0 = ''
                rlt1 = ''
                for moduleKey in allmk:
                    if moduleKey in mk:
                        result = ur.add_company_module(companyId,moduleKey,env)
                        if result['code'] == 0:
                            if moduleKey == 'M120':
                                ur.save_coupon_config(companyId,env)
                            temp_list = pdef.mkToName(moduleKey)
                            a.append(temp_list)
                            rlt0 = "  % s 模块增加完成，" % a
                        else:
                            rlt0 = '%s 模块开启失败了，原因：%s'%(moduleKey,result)
                            break
                    elif moduleKey not in mk:
                        result = ur.del_company_module(companyId,moduleKey,env)
                        if result['code'] == 0:
                            temp_list = pdef.mkToName(moduleKey)
                            b.append(temp_list)
                            rlt1 = " 未开通模块 %s，" % b
                        else:
                            rlt1 = '%s 模块删除失败了，原因：%s'%(moduleKey,result)
                            break
                rlt = rlt0+rlt1+'基础企业配置完成!'
                compInfo = qi.query_companyInfo(companyId, env)
                if compInfo['code'] == 0:
                    ds = 2
                    pu.sv_opretor_records_instdb(companyId,env,request.session.get('uid'),request.session.get('uname'),rlt,ds,msr[1])
                l[companyId] = '【'+compInfo['data']['companyName']+'】'+rlt
                mrlt = str(l)
                mrlt = mrlt.replace('{','')
                mrlt = mrlt.replace('}','')
                mrlt = mrlt.replace('\\','')
                mrlt = mrlt.replace('",','"\n')
                mrlt = mrlt.replace(' ','')
                # print(pdef.logcss(gct(),f'【saasview-basicCompCfg】'),f"转换后的结果: {m}!")
            code = c['success']
            msg = m['success']
            data = {"basicCompanyConfig": mrlt}
        bccrlt = pdef.get_result(code,msg,data)
        return jr(bccrlt)


#华为云SK企业配置
@login_required
@never_cache
def hwskset(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        print(' -- [%s] "华为云SK企业配置"'%pdef.getctime())
        if True:
            data = json.loads(request.body)
            companyIds = data["cid"]
            cname = data["cname"]
            payment = data["payment"]
            tseat = data["tseat"]
            ptseat = data["ptseat"]
            env = data["env"]
            mk = data["mk"]
            companyIds=shd(companyIds)
            # print(pdef.logcss(gct(),f'【saasview-hwskset】'),f"companyIds:{companyIds},cname:{cname},tseat:{tseat},ptseat:{ptseat}")
            hrlt = []
            hrstr = ""
            i = 0
            result = ""
            if cname:
                #修改企业名称
                for cid,cn in zip(companyIds,shd(cname)):
                    kw = {'company_name':cn}
                    ur.update_companyInfo(cid, env, **kw)
                    mcn_r = "企业名称: '%s'" %cn
                    hrlt.append(mcn_r)
            if tseat:
                #修改销售席位
                for cid,ts in zip(companyIds,shd(tseat)):
                    kw = {'seat_account':ts}
                    ur.update_companyInfo(cid, env, **kw) # 修改企业席位总数
                    mcts_r = "销售席位数:'%s'" %ts
                    hrlt.append(mcts_r)
            if ptseat:
                #修改推荐官席位
                for cid,pts in zip(companyIds,shd(ptseat)):
                    kw = {'partner_seat_account':pts}
                    ur.update_companyInfo(cid, env, **kw) # 修改企业席位总数
                    mcpts_r = "推荐官席位数:'%s'" %pts
                    hrlt.append(mcpts_r)
            while i < len(companyIds):
                cid = companyIds[i]
                ur.update_company_payment(cid, payment, env) # 修改企业付款方式
                ur.update_company_thirdparty(cid,"1",env) #修改企业的第三方人力资源id
                if int(payment) == 1: pn = "线下"
                elif int(payment) == 3: pn = "预充值"
                else: pn = payment
                mcp_r = f"打款方式:'{pn}'"
                hrlt.append(mcp_r)
                #配置企业模块
                if mk:
                    if not isinstance(mk,list): mk=shd(mk)
                    mkeys = []
                    for module_key in mk:
                        ur.add_company_module(cid,module_key,env)
                        temp_list = pdef.mkToName(module_key)
                        mkeys.append(temp_list)
                    umk_r = '添加了模块<b>%s</b> .'%mkeys
                else:
                    umk_r = ''
                hrlt.append(umk_r)
                hrstr = ",".join(hrlt)
                qci_rlt = qi.query_companyInfo(cid, env)
                try:
                    companyName = qci_rlt['data']['companyName']
                except:
                    companyName = '未知企业'
                ds = 15
                pu.sv_opretor_records_instdb(cid,env,request.session.get('uid'),request.session.get('uname'),hrstr,ds,msr[1])
                result = companyName+'('+cid+')' + ': ' + hrstr
                i += 1
            code = c['success']
            msg = m['success']
            hwskrlt = {"hwskCompanyConfig":result}
            # print(pdef.logcss(gct(),f'【saasview-hwskset】'),f'saas_hwskrlt:{hwskrlt}')

        hsrlt = pdef.get_result(code,msg,hwskrlt)
        return jr(hsrlt)


#加推salsekits版本配置
@login_required
@never_cache
def jtSaleskits(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        print(' -- [%s] "SK版本配置"'%pdef.getctime())
        if True:
            data = json.loads(request.body)
            companyIds = data['companyIds']
            mtas = data['sseats']
            mtpas = data['pseats']
            mk = data['mk']
            env = data['env']
            ctype = int(data['type'])
            srlt = ''
            for cid,mta,mtpa in zip(shd(companyIds),shd(mtas),shd(mtpas)):
                # print('cid:%s,mta:%s,mtpa:%s'%(cid,mta,mtpa))
                rlt = coa.jtSkInit(cid,mta,mtpa,env,ctype)
                if int(mta) > 1000000: mta = '无限'
                if int(mtpa) > 1000000: mtpa = '无限'
                if ctype == 0: tn = 'Saleskits'
                elif ctype == 1:
                    tn = '家装'
                    mkeys = ['M105','M109','M111','M112','M113','M131','M106']  #动态, 宣传册, 海报, 文章, 文件, 智能渠道码, 推任务
                    for mkey in mkeys:
                        ur.del_company_module(cid, mkey, env) #加装版删除未用模块
                    jzc = data['jzc']
                    if jzc=='hmy_company': remark = '红蚂蚁系统'
                    elif jzc == 'ds_company': remark = '点石系统'
                    scc = coa.saveCustomizedCode(cid,jzc,remark,env)
                    srlt += f'配置家装企业类型<b>{scc["msg"]}</b>.'
                    # print(pdef.logcss(gct(),f'【saasview-jtSaleskits】'),f'saveCustomizedCode:{scc}')
                if rlt['code'] == 0 and rlt['msg'] == '成功':
                    ic = 0
                    if mk:
                        if not isinstance(mk,list): mk=shd(mk)
                        mkeys = []
                        for module_key in mk:
                            ur.add_company_module(cid,module_key,env)
                            temp_list = pdef.mkToName(module_key)
                            mkeys.append(temp_list)
                        rt = '<b>%s版</b> 配置成功! 销售席位: <b>%s</b> ; 推荐官席位: <b>%s</b> ; 添加了模块<b>%s</b> .'%(tn,mta,mtpa,mkeys) + srlt
                    else:
                        rt = '<b>%s版</b> 配置成功! 销售席位: <b>%s</b> ; 推荐官席位: <b>%s</b> .'%(tn,mta,mtpa) + srlt
                else:
                    ic = 1
                    rt = '<b>%s版</b> 配置失败!'%tn + srlt
                compInfo = qi.query_companyInfo(cid, env)
                try:
                    companyName = compInfo['data']['companyName']
                except:
                    companyName = '未知企业'
                if ic==0:
                    ds = 3
                    pu.sv_opretor_records_instdb(cid,env,request.session.get('uid'),request.session.get('uname'),rt,ds,msr[1]) #将结果插入数据库中
                a = companyName+'【'+cid+'】: '+rt
                a = a.replace('",','"<br/>')
                a = a.replace('\\','')
            skrlt = {"skCompanyConfig":a}
            code = c['success']
            msg = m['success']
        grlt = pdef.get_result(code,msg,skrlt)
        return jr(grlt)

#销售工具版升级至salsekits版本
@login_required
@never_cache
def baseUpgradeSK(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        print(' -- [%s] "工具版升级至SK版"'%pdef.getctime())
        if True:
            data = json.loads(request.body)
            companyIds = data['companyIds']
            mtas = data['sseats']
            mtpas = data['pseats']
            mk = data['mk']
            env = data['env']
            for cid,mta,mtpa in zip(shd(companyIds),shd(mtas),shd(mtpas)):
                rlt = coa.base_upgrade_sk(cid,mta,mtpa,env)
                if rlt['code'] == 0 and rlt['msg'] == '成功':
                    ic = 0
                    if mk:
                        if not isinstance(mk,list):
                            mk=shd(mk)
                        mkeys = []
                        for module_key in mk:
                            ur.add_company_module(cid,module_key,env)
                            temp_list = pdef.mkToName(module_key)
                            mkeys.append(temp_list)
                    rt = '销售工具版升级Salskits版本成功; 销售席位: %s ; 推荐官席位: %s ; 添加了模块%s .'%(mta,mtpa,mkeys)
                else:
                    ic = 1
                    rt = '销售工具版升级Salskits版本失败, %s' %rlt['msg']
                ar = str(rt)
                compInfo = qi.query_companyInfo(cid, env)
                try:
                    companyName = compInfo['data']['companyName']
                except:
                    companyName = '未知企业'
                if ic==0:
                    ds = 8
                    pu.sv_opretor_records_instdb(cid,env,request.session.get('uid'),request.session.get('uname'),ar,ds,msr[1]) #将结果插入数据库中
                # a = compInfo['data']['companyName'] + ar
                a = companyName+'【'+cid+'】: '+ar
                a = a.replace('",','"<br/>')
                a = a.replace('\\','')
            rlt = a
            code = c['success']
            msg = m['success']
        grlt = pdef.get_result(code,msg,rlt)
        return jr(grlt)

# 更新企业信息-修改企业类型
@login_required
@never_cache
def updateCT(request):
    return redirect('/')
#更新企业信息
@never_cache
def updateCInfo(request):
    print(' -- [%s] "更新企业信息"'%pdef.getctime())
    if True:
        data = json.loads(request.body)
        cids = data['cid']
        cname = data['cname']
        admname = data['admname']
        ctype = data['ctype']
        payment = data['payment']
        etime = data['etime']
        tpid = data['tpid']
        cstatus = data['cstatus']
        rnum = data['rnum']
        tseat = data['tseat']
        ptseat = data['ptseat']
        cardids = data['cardids']
        rs = data['rs']
        env = data['env']
        print(pdef.logcss(gct(),f'【saasview-updateCInfo】'),f'cids:{cids}')
        showrlts = ""
        for cid in shd(cids):
            qci_rlt = qi.query_companyInfo(cid, env)
            if qci_rlt['code'] == 0:

                # ── 批量收集 update_companyInfo 字段，一次 HTTP 调用 ──
                info_kw = {}
                if cname and len(cids) == 1:
                    info_kw['company_name'] = cname
                elif cname and len(cids) > 1:
                    return "<p style='color:red'>WARNNING: 不支持同时修改多个企业名称！</p>"
                if admname: info_kw['admin_name'] = admname
                if ctype:   info_kw['company_type'] = ctype
                if cstatus: info_kw['company_status'] = cstatus
                if rnum:    info_kw['radar_num'] = rnum
                if tseat:   info_kw['seat_account'] = tseat
                if ptseat:  info_kw['partner_seat_account'] = ptseat

                mcn_r = man_r = mct_r = mcs_r = mcrn_r = mcts_r = mcpts_r = mcseat = ""
                if info_kw:
                    upd_rlt = ur.update_companyInfo(cid, env, **info_kw)
                    if upd_rlt['code'] != 0:
                        result = f"修改企业信息失败: {info_kw} → 原因: {upd_rlt}"
                        return result
                    # 构建结果文案
                    parts = []
                    if 'company_name' in info_kw:          parts.append(f"企业名称: '{cname}'")
                    if 'admin_name' in info_kw:            parts.append(f"管理员名称:'{admname}'")
                    if 'company_type' in info_kw:          parts.append(f"企业类型:'{ctype}'")
                    if 'company_status' in info_kw:
                        cs_map = {'0':'禁用','1':'正常','2':'注销'}
                        parts.append(f"企业状态: {cs_map.get(cstatus, cstatus)}")
                    if 'radar_num' in info_kw:             parts.append(f"雷达数:'{rnum}'")
                    if 'seat_account' in info_kw:
                        mcts_r = f"企业/销售席位数:'{tseat}'"
                        parts.append(mcts_r)
                    if 'partner_seat_account' in info_kw:
                        mcpts_r = f"推荐官席位数:'{ptseat}'"
                        parts.append(mcpts_r)
                    if tseat or ptseat:
                        mcseat = (mcts_r if tseat else "") + (mcpts_r if ptseat else "")
                    # 按旧逻辑赋值（用于后文拼接）
                    if parts:
                        mcn_r = parts[0]  # 第一个
                        for i, p in enumerate(parts):
                            if i > 0: p = "、" + p
                            if '企业名称' in parts[0] and i == 0: pass  # mcn_r done
                            elif '管理员名称' in p: man_r = p
                            elif '企业类型' in p: mct_r = p
                            elif '企业状态' in p: mcs_r = p
                            elif '雷达数' in p: mcrn_r = p
                            # seat already handled above

                # ── 独立 API（不同端点，并行调用）──
                from concurrent.futures import ThreadPoolExecutor, as_completed
                mcp_r = mcet_r = mctp_r = ""
                futures = {}
                assert_futures = bool(payment or etime or tpid)
                if assert_futures:
                    with ThreadPoolExecutor(max_workers=3) as pool:
                        if payment:
                            futures[pool.submit(ur.update_company_payment, cid, payment, env)] = "payment"
                        if etime:
                            expire_str = etime + " 23:59:59"
                            futures[pool.submit(ur.update_company_expireTime, cid, expire_str, env)] = "expire"
                        if tpid:
                            futures[pool.submit(ur.update_company_thirdparty, cid, tpid, env)] = "thirdparty"

                        for fut in as_completed(futures):
                            name = futures[fut]
                            try: resp = fut.result()
                            except Exception as e: resp = {"code": -1, "msg": str(e)}
                            if name == "payment":
                                if resp.get("code") == 0:
                                    mcp_r = f"打款方式:'{payment}'"
                                    prefix = "、" if (cname or admname or ctype) else ""
                                    mcp_r = prefix + mcp_r
                                else:
                                    result = f"修改企业打款方式'{payment}'失败了，原因：{resp}"
                                    return result
                            elif name == "expire":
                                if resp.get("code") == 0:
                                    mcet_r = f"有效期:'{expire_str}'"
                                    prefix = "、" if (cname or admname or ctype or payment) else ""
                                    mcet_r = prefix + mcet_r
                                else:
                                    result = f"修改企业有效期{etime}失败了,原因：{resp}"
                                    return result
                            elif name == "thirdparty":
                                if resp.get("code") == 0:
                                    mctp_r = f"第三方人资方id:'{tpid}'"
                                    prefix = "、" if (cname or admname or ctype or payment or etime) else ""
                                    mctp_r = prefix + mctp_r
                                else:
                                    result = f"修改企业第三方人力资源方id失败了! 原因：{resp}"
                                    return result

                #修改员工雷达状态
                if cardids and rs and len(cids)==1:
                    cardIds=shd(cardids)
                    if int(qci_rlt['code']) == 0:
                        companyType = qci_rlt['data']['companyType']
                        mcrs = ur.updata_radar_status(cid, cardIds, rs, companyType, env)
                        if mcrs['code'] == 0:
                            rlt2= qi.query_cardInfo(cardIds, env)
                            i = 0
                            cns = []
                            rss = []
                            while i < len(cardIds):
                                radarStatus = rlt2['data'][i]['radarStatus']
                                rss.append(radarStatus)
                                cardName = rlt2['data'][i]['cardName']
                                cns.append(cardName)
                                i += 1
                            b=len(set(rss))
                            if rlt2['code'] == 0 and b == 1 and str(rss[0]) == rs:
                                if int(rs) == 0:
                                    ncrs_r = "员工%s的'雷达'关闭" %cns
                                elif int(rs) == 1:
                                    ncrs_r = "员工%s的'AI雷达'开启" %cns
                                elif int(rs) == 3:
                                    ncrs_r = "员工%s的'AI雷达和BOSS雷达'开启" %cns
                            elif rlt2['code'] != 0:
                                result = "查询员工信息接口异常: %s"%rlt2
                                return result
                            elif b != 1:
                                result = "修改员工雷达信息不一致: %s"%rss
                                return result
                            else:
                                result = "员工雷达状态(%s)与接口查询(%s)不一致!"%(rss,rs)
                                return result
                        else:
                            result = "修改员工雷达状态失败了!%s" %mcrs
                            return result
                    else:
                        result = '获取companyType异常: %s'%qci_rlt
                        return result
                elif cardids and rs and len(cids) >1:
                    return "<p style='color:red'>WARNNING: 不支持同时修改多个企业管理员名称！</p>"
                else:
                    ncrs_r=''
                if (cname or admname or ctype or payment or etime or tpid or cstatus or rnum or tseat or ptseat) and cardids:
                    rlt = '修改企业信息' + '【' + mcn_r + man_r + mct_r + mcp_r + mcet_r + mctp_r + mcs_r + mcrn_r + mcseat + '、' + ncrs_r + '】成功了!'
                else:
                    rlt = '修改企业信息' + '【' + mcn_r + man_r + mct_r + mcp_r + mcet_r + mctp_r + mcs_r + mcrn_r + mcseat + ncrs_r + '】成功了!'
                try:
                    companyName = qci_rlt['data']['companyName']
                except:
                    companyName = '未知企业'
                ds = 4                
                pu.sv_opretor_records_instdb(cid,env,request.session.get('uid'),request.session.get('uname'),rlt,ds,msr[1])
                showrlt = companyName+'('+cid+')' + ': ' + rlt
            else:
                showrlt='查询企业信息接口异常(请确认环境是否正确): %s'%qci_rlt
            showrlts += showrlt + '<br/>'
    rlt = showrlts
    code = c['success']
    msg = m['success']
    grlt = pdef.get_result(code,msg,rlt)
    return jr(grlt)

@login_required
@never_cache
def companyModule(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        print(' -- [%s] "更新企业模块"'%pdef.getctime())
        if True:
            data = json.loads(request.body)
            # print(pdef.logcss(gct(),f'【saasview-companyModule】'),f'前端入参的data:{data}')
            companyIds = data['companyId']
            mk = data['mk']
            cm = data['cm']
            env = data['env']
            companyIds=shd(companyIds)
            l = {}
            rlt = ''
            ds = 5
            ic = 0
            mk = [x for x in shd(mk) if x]
            if cm == 'addm':
                for companyId in companyIds:
                    a, a0, b0 = [], [], [] #必须放在循环内，每次循环时，才能清空之前的数据
                    rlt0,rlt1,rlt2 = '', '', ''
                    for moduleKey in mk:
                        qcm_rlt0 = qi.query_companyModule(companyId, env)
                        if qcm_rlt0:
                            qcm_data = qcm_rlt0['data']
                        else: qcm_data = []
                        if moduleKey in qcm_data:
                            rlt0 = ''
                            noreq = pdef.mkToName(moduleKey)
                            b0.append(noreq)
                            if b0:
                                rlt0 = '%s模块已开通,无需重复开通.' %b0
                        elif moduleKey not in qcm_data:
                            rlt1 = ''
                            rlt2 = ''
                            result = ur.add_company_module(companyId,moduleKey,env)
                            if result['code'] == 0:
                                if moduleKey == 'M120':
                                    ur.save_coupon_config(companyId,env)
                                temp_list = pdef.mkToName(moduleKey)
                                a.append(temp_list)
                                if a:
                                    rlt1 = "  % s 模块增加成功啦!" % a
                            elif result['code'] == 77001:
                                ic = 1
                                rlt2 = "添加模块接口调用异常！"
                            else:
                                temp_list = pdef.mkToName(moduleKey)
                                a0.append(temp_list)
                                if a0:
                                    rlt2 = "  % s 模块增加失败了!" % a0
                    rlt = rlt0 + rlt1 + rlt2
                    # print(pdef.logcss(gct(),f'【saasview-companyModule】'),f'增加模块情况:{rlt}')
                    if ic == 0:
                        pu.sv_opretor_records_instdb(companyId,env,request.session.get('uid'),request.session.get('uname'),rlt,ds,msr[1])
                    companyName = qi.query_companyName(companyId,env)
                    l[companyId] = '【'+companyName+'】'+rlt
            elif cm == 'delm':
                for companyId in companyIds:
                    a, a0, b0 = [], [], [] #必须放在循环内，每次循环时，才能清空之前的数据
                    rlt0,rlt1,rlt2 = '', '', ''
                    for moduleKey in mk:
                        qcm_rlt0 = qi.query_companyModule(companyId, env)
                        if qcm_rlt0:
                            qcm_data = qcm_rlt0['data']
                        else: qcm_data = []
                        if qcm_data:
                            if moduleKey not in qcm_data:
                                rlt0 = ''
                                noreq = pdef.mkToName(moduleKey)
                                b0.append(noreq)
                                if b0:
                                    rlt0 = '%s模块未开通,无需删除.' %b0
                            else:
                                rlt1 = ''
                                rlt2 = ''
                                result = ur.del_company_module(companyId,moduleKey,env)
                                # print("000000 delete module key:",result)
                                if result['code'] == 0:
                                    temp_list = pdef.mkToName(moduleKey)
                                    a.append(temp_list)
                                    if a:
                                        rlt1 = "  % s 模块删除成功啦!" % a
                                elif result['code'] == 77002:
                                    ic = 1
                                    rlt2 = "关闭模块接口调用异常！"
                                else:
                                    temp_list = pdef.mkToName(moduleKey)
                                    a0.append(temp_list)
                                    if a0:
                                        rlt1 = "  % s 模块删除失败了!" % a0
                        else:
                            ic = 1
                            rlt0 = "查询企业模块接口异常"
                            rlt1, rlt2 = "", ""
                    rlt= rlt1+ rlt0 + rlt2
                    # print(pdef.logcss(gct(),f'【saasview-companyModule】'),f'删除模块情况:{rlt}')
                    if ic == 0:
                        pu.sv_opretor_records_instdb(companyId,env,request.session.get('uid'),request.session.get('uname'),rlt,ds,msr[1])
                    companyName = qi.query_companyName(companyId,env)
                    l[companyId] = '【'+companyName+'】'+rlt
            mrlt = str(l)
            mrlt = mrlt.replace('{','')
            mrlt = mrlt.replace('}','')
            mrlt = mrlt.replace('\\','')
            mrlt = mrlt.replace("'[","")
            mrlt = mrlt.replace("]'","")
            mrlt = mrlt.replace(' ','')
            # print(pdef.logcss(gct(),f'【saasview-companyModule】'),f'调整格式后的结果:{m}')
            code = c['success']
            msg = m['success']
        grlt = pdef.get_result(code,msg,mrlt)
        return jr(grlt)

# 激活注销的手机号
@never_cache
def removeTagTel(request):
    print(' -- [%s] "辅助工具-激活注销的手机号"'%pdef.getctime())
    data = json.loads(request.body)
    tel = data['phoneNumber']
    env = data['env']
    rtt = ur.remove_tagTel(tel,env)
    if rtt['code'] == 0:
        rlt = "激活成功！"
    else:
        rlt = "激活失败，原因：%s" %rtt
    r = str(tel)+": "+rlt
    companyId = 0
    ds = 12
    pu.sv_opretor_records_instdb(companyId,env,request.session.get('uid'),request.session.get('uname'),r,ds,msr[1]) #操作记录入库
    code = c['success']
    msg = m['success']
    gr = pdef.get_result(code,msg,r)
    return jr(gr)

@never_cache
def delclueinfo(request):
    print(' -- [%s] "辅助工具-删除线索"'%pdef.getctime())
    if True:
        data = json.loads(request.body)
        companyId = data['companyId']
        ppc = data['ppc']
        env = data['env']
        check = data['check']
        if check == 'del':
            userid = data['userId']
            delcheck = data['delcheck']
            if userid:
                userid=shd(userid)
                for nuid in userid:
                    rlt = jtk.delchecked(companyId,str(nuid),env,delcheck,ppc)
                    if '删除成功' in rlt:
                        ds = 444
                        pu.sv_opretor_records_instdb(companyId,env,request.session.get('uid'),request.session.get('uname'),rlt,ds,msr[1]) #操作记录入库
            else:
                rlt = '"用户ID"不能为空！'
        else:
            rlt = "类型错误，check = ", check
        code = c['success']
        msg = m['success']

    grlt = pdef.get_result(code,msg,rlt)
    return jr(grlt)

#辅助工具--删除线索/合伙人数据
@login_required
@never_cache
def delCP(request):
    return redirect('/')

#根据手机号查看userId
@never_cache
def queryuibycp(request):
    print(' -- [%s] "辅助工具-据手机号查userId和parnterId"'%pdef.getctime())
    if True:
        data = json.loads(request.body)
        cid = data['cid']
        tel = data['tel']
        env = data['env']
        rlt = qi.query_uidbyCP(cid,tel,env)
        if rlt['code'] == 0 and rlt['msg'] == '成功' and rlt['data'] != None:
            a = rlt['data']['userId']
        else:
            a = '查询结果为%s, 请确认手机号和环境是否正确! '%rlt['data']
        qpid = qi.query_pidbyCP(cid,tel,env)
        if qpid['code']==0 and qpid['data'] is not None:
            b = qpid['data']['partnerId']
        else:
            b = ''
        qurlt={"userId":a,"partnerId":b}
        code = c['success']
        msg = m['success']

    gr = pdef.get_result(code,msg,qurlt)
    return jr(gr)

#销售添加线索
@never_cache
def saci(request):
    print(' -- [%s] "辅助工具-销售添加线索"'%pdef.getctime())
    if True:
        data = json.loads(request.body)
        cid = data['cid']
        cardid = data['cardid']
        uname = data['uname']
        utel = data['utel']
        bn = data['bn']
        pId = data['pId']
        env = data['env']
        if bn == 1:
            rlt = pdef.saleAddClue(cid,cardid,uname,utel,pId,env)
            if rlt['code'] == 0 and rlt['msg'] == "成功":
                userid = rlt['data']['userId']
                r = '添加成功=>%s:(userId)%s'%(utel,userid)
            else:
                r = '添加失败=>%s:%s'%(utel,rlt['msg'])
        else:
            y = 0
            uts = []
            uns = []
            rr = []
            while y < int(bn):
                ut = int(utel) + y #手机号生成
                x = 5
                while x>=0:
                    lastun = uname[-x:]
                    isint = lastun.isdigit() #isdigit() 检测字符串是否只由数字组成，是则返回Ture,否则返回Flase
                    if isint:
                        un = uname[:-x]+str(int(lastun)+y)
                        # print(pdef.logcss(gct(),f"【saasview-saci】"),f'拼接的新username:{un}')
                        break
                    else:
                        x-=1
                        if x == 0:
                            un = uname + str(y)
                y += 1
                uts.append(str(ut))
                uns.append(un)
            for usertel,username in zip(uts,uns):
                rlt = pdef.saleAddClue(cid,cardid,username,usertel,pId,env)
                if rlt['code'] == 0 and rlt['msg'] == "成功":
                    userid = rlt['data']['userId']
                    r0 = '添加成功=>%s:(userId)%s'%(usertel,userid)
                else:
                    r0 = '添加失败=>%s:%s'%(usertel,rlt['msg'])
                # rr[usertel]=r0
                rr.append(r0)
            r = str(rr).replace(',','\n')
            r = r.replace('[',' ')
            r = r.replace(']','')
        code = c['success']
        msg = m['success']
    grlt = pdef.get_result(code,msg,r)
    return jr(grlt)

#设置合伙人登录APP验证码
@never_cache
def splc(request):
    print(' -- [%s] "辅助工具-设置合伙人登录APP验证码"'%pdef.getctime())
    if True:
        data = json.loads(request.body)
        tel = data['tel']
        code = data['code']
        env = data['env']
        role = data['role']
        if role == 'sale':
            cid = data['cid']
            rlt1 = pdef.salesLoginCodeReset(cid,tel,code,env)
            if rlt1['code'] == 0:
                r = '【%s】: %s修改登录验证码为%s成功！'%(cid,tel,code)
            else:
                r = '%s修改登录验证码失败！，失败原因：%s'%(tel,rlt1['msg'])
        elif role== 'partner':
            rlt = pdef.setPantnerLoginCode(tel,code,env)
            if rlt['code'] == 0 and rlt['msg'] == '成功':
                r = '【推荐官】%s修改登录验证码为%s成功！'%(tel,code)
            else:
                r = '%s修改登录验证码失败！，失败原因：%s'%(tel,rlt['msg'])
        code = c['success']
        msg = m['success']
    grlt = pdef.get_result(code,msg,r)
    return jr(grlt)

#根据起始和结束位截取dict
def getdict(adict, start, end):
    keys = adict.keys()
    a = {}
    for k in list(keys)[start:end]:
        a[k] = adict[k]
    alen = len(a)
    return a,alen

#辅助工具--企业微信相关
@login_required
@never_cache
def forWechatCom(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        print(' -- [%s] "辅助工具-企业微信相关"'%pdef.getctime())
        if True:
            data = json.loads(request.body)
            type = data['type']
            env = data['env']
            if type == 1: #生成企微应用链接
                companyId = data['companyId']
                appId = data['appId']
                rlt = fwc.getWeComAppAuthorLink(companyId,appId,env)
            elif type == 2: #获取密文企微ID
                corpId = data['corpId']
                rlt = fwc.getOpenCorpId(corpId,env)
            elif type == 3: #清除公众号/小程序绑定数据
                companyIds = data['companyId']
                appId = data['appId']
                status = data['status']
                rlt = fwc.delAppletConfig(companyIds,appId,status,env)
                if "数据成功" in rlt:
                    ds = 6
                    a= rlt.split(': ',1)
                    pu.sv_opretor_records_instdb(companyIds,env,request.session.get('uid'),request.session.get('uname'),a[1],ds,msr[1])
            code = c['success']
            msg = m['success']
        grlt = pdef.get_result(code,msg,rlt)
        return jr(grlt)

#辅助工具--手工合并企业用户
@login_required
@never_cache
def mergeUser(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        print(' -- [%s] "辅助工具-手工合并企业用户"'%pdef.getctime())
        if True:
            data = json.loads(request.body)
            companyId = data['companyId']
            openIds = data['opids']
            env = data['env']
            openIds=shd(openIds)
            allrlt = {}
            for openId in openIds:
                rlt = pdef.mergeUserByHand(companyId,openId,env)
                if rlt['code'] == 0 and rlt['msg'] == '成功':
                    r = '用户合并成功!'
                else:
                    r = '用户合并失败!'
                allrlt[openId]=r
            allrlt = str(allrlt)
            result = {"a":allrlt}
            try:
                qci_rlt = qi.query_companyInfo(companyId, env) #调用查询企业信息接口
            except:
                qci_rlt = 'null'
            if qci_rlt == 'null':
                cn = iaq.query_cnbycid(companyId,env)
                if len(cn) == 0:
                    cname = '企业已冻结或已注销'
                else:
                    cname = cn["company_name"]
            else:
                cname = qci_rlt['data']['companyName']
            ds = 7
            pu.sv_opretor_records_instdb(companyId,env,request.session.get('uid'),request.session.get('uname'),allrlt,ds,msr[1])
            code = c['success']
            msg = m['success']
        grlt = pdef.get_result(code,msg,result)
        return jr(grlt)

#辅助工具--清除过期企业信息数据
@login_required
@never_cache
def delBindRelation(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        print(' -- [%s] "辅助工具-清除过期企业信息数据"'%pdef.getctime())
        if True:
            data = json.loads(request.body)
            companyIds = data['companyIds']
            companyIds = shd(companyIds)
            env = data['env']
            rl = []
            for companyId in companyIds:
                try:
                    qci_rlt = qi.query_companyInfo(companyId, env) #调用查询企业信息接口
                except:
                    qci_rlt = 'null'
                if qci_rlt == 'null':
                    cn = iaq.query_cnbycid(companyId,env)
                    if len(cn) == 0:
                        cname = '企业已冻结或已注销'
                    else:
                        cname = cn["company_name"]
                else:
                    cname = qci_rlt['data']['companyName']
                rlt = pdef.delBindReltionship(companyId,env)
                if rlt['code'] == 0 and rlt['msg'] == '成功':
                    r0 = '清除过期企业数据成功! '
                    ds = 9
                    pu.sv_opretor_records_instdb(companyId,env,request.session.get('uid'),request.session.get('uname'),r0,ds,msr[1])
                else:
                    r0 = rlt['msg']
                rl.append(cname+'('+str(companyId)+'): '+r0)
                rl = str(rl)
                rl = rl.replace('",','"<br/>')
                rl = rl.replace('\\','')
                r = rl[1:-1]
            code = c['success']
            msg = m['success']
        grlt = pdef.get_result(code,msg,r)
        return jr(grlt)

#辅助工具--清除app登录token
@login_required
@never_cache
def cleanAppToken(request):
    print(' -- [%s] "辅助工具-清除app登录token"' % pdef.getctime())
    data = json.loads(request.body)
    companyId = data['companyId']
    env = data['env']
    try:
        rlt = ur.clean_appLoginToken(companyId, env)
        if rlt and rlt.get('code') == 0:
            res = '清除app登录token成功!'
        else:
            res = rlt.get('msg', '操作失败') if rlt else '操作失败'
        code = c['success'] if (rlt and rlt.get('code') == 0) else c['reserror']
        msg = m['success'] if (rlt and rlt.get('code') == 0) else m['reserror']
    except Exception as e:
        res = f"接口异常: {e}"
        code = c['reserror']
        msg = m['reserror']
    grlt = pdef.get_result(code, msg, res)
    return jr(grlt)

#辅助工具--查询登录验证码
@login_required
@never_cache
def queryLoginCode(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        print(' -- [%s] "辅助工具-查询登录验证码"'%pdef.getctime())
        data = json.loads(request.body)
        env = data['env']
        tel = data['tel']
        rlt = gc.verification_code(env,tel)
        code = c['success']
        msg = m['success']
        gr = pdef.get_result(code,msg,rlt)
        return jr(gr)

#辅助工具--定制企业功能
@login_required
@never_cache
def dzFunction(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        print(' -- [%s] "辅助工具-定制企业功能"'%pdef.getctime())
        if True:
            data = json.loads(request.body)
            env = data["env"]
            type = data["type"]
            rlt = ""
            if type == "hmyupdcs":
                cfid = data["cfid"]
                fs = int(data["fs"])
                hufsrlt = dzf.hmy_updateFollowStatus(cfid,fs,env)
                if hufsrlt["code"] == 0:
                    getCD = dzf.hmy_queryCustDetailByCFID(cfid,env)
                    cid = getCD["data"]["companyId"]
                    custname = getCD["data"]["name"]
                    getfs = dzf.queryFollowStatus(cid,env)
                    fsn = getfs["data"][fs]["statusName"]
                    rlt = "客户“%s”修改阶段为“%s”!"%(custname, fsn)
                    ds = 16
                    pu.sv_opretor_records_instdb(cid,env,request.session.get('uid'),request.session.get('uname'),rlt,ds,msr[1])
                else:
                    rlt="红蚂蚁企业更新阶段失败，%s"%hufsrlt["msg"]
                # print(pdef.logcss(gct(),f"【saasview-dzFunction】"),f'红蚂蚁企业的客户更新阶段: {rlt}')
            elif type == "hwylicensejh":
                compId = data["compid"]
                lisence = data["lisence"]
                remark = data["remark"]
                hrlrlt = dzf.hwy_registLisence(compId,lisence,env)
                ds = 13 #华为lisence激活
                if hrlrlt["code"] == 0:
                    rlt = "lisence【%s】激活成功! "%lisence + remark
                else:
                    rlt = "lisence【%s】激活失败! "%lisence
                pu.sv_opretor_records_instdb(compId,env,request.session.get('uid'),request.session.get('uname'),rlt,ds,msr[1])
            code = c['success']
            msg = m['success']
        grlt = pdef.get_result(code,msg,rlt)
        return jr(grlt)

#辅助工具--批量删除用户数据
@login_required
@never_cache
def batchDeleteClue(request):
    if request.method == 'GET':
        return redirect('/')
    else:
        data = json.loads(request.body)
        cid = data["cid"]
        phones = data["phones"]
        env = data["env"]
        phonesList = shd(phones)
        i = 0
        failPhones = []
        for phone in phonesList:
            i += 1
            rlt = qi.query_uidbyCP(cid,phone,env)
            print(f"query userInfo: {rlt}")
            try:
                data = rlt['data']
                userId = data['userId']
                # print("【%s】查询uid(%s)结果: %s"%(phone,i,userId))
                delcheck = 'delclue'
                durlt = jtk.delchecked(cid,userId,env,delcheck)
                print("删除结果:",durlt)
            except Exception as e:
                # print("查询用户数据error:",e)
                failPhones.append(phone)
        rlt = f"【{cid}】总执行的手机号数为: {len(phonesList)} ; 执行失败的手机号数为: {len(failPhones)} , 手机号为: {failPhones} ."
        code = c['success']
        msg = m['success']
        qrlt = pdef.get_result(code,msg,rlt)
        return jr(qrlt)

# AFTERSALES
@login_required
@never_cache
def afterSales(request):
    if request.method == 'GET':
        return redirect('/')
#查询企业ID
@never_cache
def queryCompanyId(request,sysvs):
    if True:
        data = json.loads(request.body)
        loginName = data['ln']
        env = data["env"]
        if sysvs == "saas":
            if len(loginName) == 11:
                qln = qe.query_companyId(loginName,env)
                if qln['code'] == 0 and qln["data"]:
                    cid = qln['data']['companyId']
                    cn = qln['data']['companyName']
                    phone = loginName
                    rlt = {"cn":cn,"cid":cid,"phone":phone}
                    code = c['success']
                    msg = m['success']
                else:
                    rlt = '查询异常: %s'%qln["msg"]
                    code = c['nodata']
                    msg = m['nodata']
            else:
                qci = qe.query_companyInfoByCompanyId(loginName,env)
                if qci['code'] == 0 and qci["data"]:
                    cid = qci['data']['companyId']
                    cn = qci['data']['companyName']
                    phone = qci['data']['loginName']
                    rlt = {"cn":cn,"cid":cid,"phone":phone}
                    code = c['success']
                    msg = m['success']
                else:
                    rlt = '查询异常: %s'%qci["msg"]
                    code = c['nodata']
                    msg = m['nodata']

        elif sysvs == "origin":
            qln = iaq.query_cidbyphone(loginName,env)
            # print(pdef.logcss(gct(),f"【saasview-queryCompanyId】"),f'query_cidbyphone: {qln}')
            if qln:
                for i in qln:
                    cid = i["company_id"]
                    cn = i["company_name"]
                    rlt = {"cn":cn,"cid":cid}
            else:
                rlt = "未查到企业ID。"
            code = c['success']
            msg = m['success']
    qrlt = pdef.get_result(code,msg,rlt)
    return jr(qrlt)
    
# 查询企微ID
@never_cache
def queryCI(request):
    data = json.loads(request.body)
    companyId = data['companyId']
    qci = qi.query_companyInfo(companyId, env = 'prod')
    if qci['code'] == 0 and qci['data'] != None and qci['data'] != NULL and qci['data'] != '':
        qca = qe.query_corpAuth(companyId)
        if qca['code'] == 0:
            if qca['data']['autho']['cpe_tong'] == 0 or qca['data']['autho']['cpe_backlog'] == 0: #校验企业是否有绑通讯录或自建应用
                result = qe.query_cropId(companyId) #查询企业微信ID
                if result['code'] == 0:
                    rlt = result['data']
                    a = '%s: %s' %(companyId,rlt)
                else:
                    a = str(companyId)+': 查询企业微信ID接口异常!'
            else:
                a = str(companyId)+': 通讯录和自建应用未授权，无法查询企业微信ID!'
        else:
            a = str(companyId)+': 查询企微应用接口异常.'
        # print(pdef.logcss(gct(),f'【saasview-queryCI】'),f'企微id为 {a}')
    elif qci['code'] == 0 and qci['data'] == None:
        a = '企业不存在或企业已过期.'
    else:
        a = '企业ID查询异常!'
    
    code = c['success']
    msg = m['success']
    gr = pdef.get_result(code,msg,a)
    return jr(gr)

# 查询明文查询密文企微ID
@never_cache
def querySCID(request):
    data = json.loads(request.body)
    corpId = data['companyId']
    oci = qe.openCorpId(corpId)
    if oci['code'] == 0 and oci['msg'] == '成功':
        if oci['data']['errcode'] == 0:
            rlt = "企微ID(密文): "+oci['data']['open_corpid']
        else:
            rlt = "企微ID错误，请输入正确的企微ID! "
    else:
        rlt = '获取加密企微ID异常，',oci
    
    code = c['success']
    msg = m['success']
    gr = pdef.get_result(code,msg,rlt)
    return jr(gr)

#查询小程序、公众号、通讯录、雷达、自建应用绑定状态
@never_cache
def queryCA(request):
    data = json.loads(request.body)
    companyId = data['companyId']
    qci = qi.query_companyInfo(companyId, env = 'prod')
    if qci['code'] == 0 and qci['data'] != None and qci['data'] != NULL and qci['data'] != '':
        qca = qe.query_corpAuth(companyId)
        if qca['code'] == 0:
            qca_result = qca['data']['autho']
            # print(pdef.logcss(gct(),f'【saasview-queryCA】'),f'查询企微应用接口autho: {qca_result}')
            if qca_result['card'] == 0:
                qca_result['card'] = "<span style='color:green;font-weight:600;'>已绑定</span>"
            else:
                qca_result['card'] = "<span style='color:red;'>未绑定</span>"
            if qca_result['wx_oa'] == 0:
                qca_result['wx_oa'] = "<span style='color:green;font-weight:600;'>已绑定</span>"
            elif qca_result['wx_oa'] == 2:
                qca_result['wx_oa'] = "<span style='color:yellow;font-weight:600;'>加推授权</span>"
            else:
                qca_result['wx_oa'] = "<span style='color:red;'>未绑定</span>"
            code = c['success']
            msg = m['success']
            rlt = "%s：小程序-%s；公众号-%s。"%(qci['data']['companyName'],qca_result['card'],qca_result['wx_oa'])
        else:
            code = c['reserror']
            msg = m['reserror']
            rlt = '查询企微应用接口异常.'
    elif qci['code'] == 0 and qci['data'] == None:
        code = c['nodata']
        msg = m['nodata']
        rlt = qci['msg']
    else:
        code = c['reserror']
        msg = m['reserror']
        rlt = '企业ID查询异常!'
    gr = pdef.get_result(code,msg,rlt)
    return jr(gr)

# /agent/authAppList
# 查询企业已授权的企微应用
@never_cache
def queryAAL(request):
    data = json.loads(request.body)
    companyId = data['companyId']
    qci = qi.query_companyInfo(companyId, env = 'prod')
    if qci['code'] == 0 and qci['data'] != None and qci['data'] != NULL and qci['data'] != '':
        qaal = qe.query_authAppList(companyId)
        if qaal['code'] == 0:
            if qaal["data"] == []:
                rlt = '%s未绑定应用. ' %qci['data']['companyName']
            else:
                qaal_result = qaal['data']
                j = []
                for i in qaal_result:
                    j.append(i['appName'])
                
                code = c['success']
                msg = m['success']
                rlt = "“%s”已绑应用：%s. " %(qci['data']['companyName'],j)
        else:
            code = c['reserror']
            msg = m['reserror']
            rlt = '查询应用接口异常.'
    elif qci['code'] == 0 and qci['data'] == None:
        code = c['nodata']
        msg = m['nodata']
        rlt = qci['msg']
    else:
        code = c['reserror']
        msg = m['reserror']
        rlt = '企业ID查询异常!'
    gr = pdef.get_result(code,msg,rlt)
    return jr(gr)

#绑定企业和企微加密corpid
@never_cache
def selfcreatedCS(request):
    data = json.loads(request.body) #获取ajax提交页面的data4的数据
    companyId = data['companyId']
    corpId = data['corpId']
    sccs = qe.selfcreated_configSave(companyId,corpId)
    if sccs['code'] == 0 and sccs['msg'] == "成功":
        rlt = '企业[%s]与企微corpId[%s]绑定成功!'%(companyId,corpId)
    else:
        rlt = '绑定失败: %s'%sccs['msg']
    env = 'prod'
    ds = 10
    pu.sv_opretor_records_instdb(companyId,env,request.session.get('uid'),request.session.get('uname'),rlt,ds,msr[1]) #操作记录入库
    code = c['success']
    msg = m['success']
    gr = pdef.get_result(code,msg,rlt)
    return jr(gr)

#配置小程序隐私保护
@never_cache
def privset(request):
    data = json.loads(request.body) #获取ajax提交页面的数据
    companyId = data['companyId']
    try:
        qci = qi.query_companyInfo(companyId, env = 'prod') #查询企业信息
        cname = qci["data"]["companyName"]
        ps = qe.privacy_setting(companyId)
        qmt = iaq.query_message_total(({}, f'data_source=11 and company_id={companyId} and'))
        ps_result = f'{ps["msg"]}, 该企业已配置隐私保护{qmt["c"]+1}次。'
        # print(pdef.logcss(gct(),f'【saasview-queryCA】'),f"配置隐私保护接口msg: {ps_result}")
        psrlt = '配置隐私保护'+ps_result
        rlt = str(companyId)+': '+psrlt
        pu.sv_opretor_records_instdb(companyId,'prod',request.session.get('uid'),request.session.get('uname'),psrlt,11,msr[1],cname) #操作记录入库
        code = c['success']
        msg = m['success']
    except Exception as e:
        code = c['reserror']
        msg = m['reserror']
        rlt = '企业信息查询异常, 原因: ' + e
    gr = pdef.get_result(code,msg,rlt)
    return jr(gr)

#定制化小程序配置保存
@never_cache
def dzconfig(request):
    data = json.loads(request.body) #获取ajax提交页面的data4的数据
    companyId = data['companyId']
    appletCorpId = data['corpId']
    appletSecretKey = data['secretKey']
    applet = data['applet']
    istest = data['istest']
    if istest: env = "test"
    else: env = "prod"
    if applet in ("zs","dz"):
        dcs = qe.dzapplet_config_save(companyId,appletCorpId,appletSecretKey,applet,env)
        if dcs['code'] == 0:
            dcs_result = dcs['msg']
            if applet == 'zs': ap = "招商版"
            elif applet == "dz": ap = "转介绍版"
            rlt = str(companyId)+'【定制化小程序配置】: 绑定“%s”小程序【APPID(%s), SECRET(%s)】%s !'%(ap,appletCorpId,appletSecretKey,dcs_result)
            dbrlt = '【定制化小程序配置】: 绑定“%s”小程序【APPID(%s), SECRET(%s)】%s !'%(ap,appletCorpId,appletSecretKey,dcs_result)
            pu.sv_opretor_records_instdb(companyId,env,request.session.get('uid'),request.session.get('uname'),dbrlt,'12',msr[1]) #操作记录入库
            code = c['success']
            msg = m['success']
        else:
            code = c['reserror']
            msg = m['reserror']
            rlt = '接口异常，%s.' %dcs['msg']
    elif applet == "org":
        owairlt = ovs.origin_saveOrUpdateWxAppInfo(companyId,appletCorpId,appletSecretKey,env)
        if owairlt['code'] == 0 and owairlt['data']:
            rlt = '基线版企业（%s）绑定小程序【APPID(%s), SECRET(%s)】成功! '%(companyId,appletCorpId,appletSecretKey)
            pu.sv_opretor_records_instdb(companyId,env,request.session.get('uid'),request.session.get('uname'),rlt,'102',msr[1],"",3)
            code = c['success']
            msg = m['success']
        else:
            code = c['reserror']
            msg = m['reserror']
            rlt = '企业绑定小程序异常, '+owairlt['msg']
        pass
    else:
        code = c['nodata']
        msg = m['nodata']
        rlt = ''
    gr = pdef.get_result(code,msg,rlt)
    return jr(gr)

dsname = {1:'utsj',2:'bssj',3:'sksj',4:'ucisj',15:'hwsksj'}

@never_cache
def getappid(request):
    data = json.loads(request.body)
    cid = data['cid']
    env = data['env']
    garlt = mp.getappidbycid(cid,env)
    rlt = {"appid": garlt['data']}
    code = c['success']
    msg = m['success']
    gr = pdef.get_result(code,msg,rlt)
    return jr(gr)

@login_required
@never_cache
def miniprogram(request):
    return redirect('/')

@never_cache
def miniprogramRelease(request,type):
    data = json.loads(request.body)
    type = data['type']
    env = data['env']
    phone = data['phone']
    cid = data['cid']
    cn = data['cn']
    appid = data['appid']
    code = c['success']
    msg = m['success']
    isinst = True
    if type == "baconfig":
        tsq = data['tsq']
        template_id = data.get('template_id', '535')
        template_version = data.get('template_version', 'v4.3.0')
        template_desc = data.get('template_desc', 'vr配置')
        custom_domains = data.get('domains', [])
        mp.gettoken(cid,env)
        tsq = [x for x in shd(tsq) if x]
        rlt = ""
        errtips = ""
        for tsqs in tsq:
            if rlt: rlt += ", "
            if "priv" == tsqs:
                ps = qe.privacy_setting(cid)
                if ps["msg"] == "成功":
                    rlt += "隐私权限配置成功"
            elif "ulcm" == tsqs:
                ucmrlt = mp.wxacommit(cid,env,appid,template_id,template_version,template_desc)
                if ucmrlt['errcode'] == 0:
                    rlt += "上传代码模板成功"
            elif "addm" == tsqs:
                # 合并默认域名和用户自定义域名（去重）
                default_domain = "https://dsa-app.aijiatui.com"
                all_domains = list(set([default_domain] + [d.strip() for d in custom_domains if d.strip()]))
                dmss = iaq.query_domain_status(appid)
                if not dmss:
                    smd = mp.setmodifydomain()
                    smdec = str(smd["errcode"])
                    swd= mp.setwebviewdomain(all_domains)
                    swdec = str(swd["errcode"])
                    if smdec == "0" and swdec == "0":
                        rlt += '添加域名成功'
                        iaq.inst_domain_status(cid,appid,3)
                    elif smdec == "0" and swdec != "0":
                        rlt += '仅添加服务器域名成功'
                        iaq.inst_domain_status(cid,appid,1)
                    elif smdec != "0" and swdec == "0":
                        rlt += '仅添加业务域名成功'
                        iaq.inst_domain_status(cid,appid,2)
                    else:
                        print(f"服务器域名: {mp.errorcode(smdec)}; 业务域名: {mp.errorcode(swdec)}")
                        rlt += "添加域名失败"
                    if swdec in ("89020","89021","86103"):
                        errtips = "业务域名配置失败，请先配置业务域名校验文件！"
                elif dmss:
                    if dmss['status'] == "1":
                        swd= mp.setwebviewdomain(all_domains)
                        swdec = str(swd["errcode"])
                        if swdec == "0":
                            rlt += '添加域名成功'
                            iaq.update_domain_status(3,dmss['id'])
                        if swdec in ("89020","89021","86103"):
                            errtips = "业务域名配置失败，请先配置业务域名校验文件！"
                    elif dmss['status'] == "2":
                        smd = mp.setmodifydomain()
                        smdec = str(smd["errcode"])
                        if smdec == "0":
                            rlt += '添加域名成功'
                            iaq.update_domain_status(3,dmss['id'])
                    elif dmss['status'] == "3":
                        rlt += '添加域名成功'
            print("rltrltrlt:",rlt)
        rltd = {"rlt":rlt,"errtips":errtips}
    elif type == "getwdcfile":
        isinst = False
        gwc = mp.get_webviewdomain_confirmfile()
        if gwc['errcode'] == 0: rlt = gwc
        else:
            code = c['reserror']
            msg = m['reserror']
            rlt = f"下载失败，原因: {mp.errorcode(gwc['errcode'])}"
        rltd = {"rlt":rlt}
        print("rltddddddd000000000:",rltd)
    elif type == "auditAndRelease":
        ts = data['ts']
        print("000000:",ts)
        if ts == "audit":
            gc = mp.getcategory(cid,env)
            # print("auditAndRelease-getcategory:",gc)
            clist = gc["categories"]
            newlist = []
            # 遍历修改每个字典
            for item in clist:
                if item["audit_status"] == 3:
                    # 重命名 first → first_id
                    if "first" in item:
                        item["first_id"] = item.pop("first")
                    # 重命名 second → second_id
                    if "second" in item:
                        item["second_id"] = item.pop("second")
                    if "first_name" in item:
                        item["first_class"] = item.pop("first_name")
                    if "second_name" in item:
                        item["second_class"] = item.pop("second_name")
                    # 移除 audit_status 字段（无论是否存在都不报错）
                    item.pop("audit_status", None)
                    newlist.append(item)
            sa = mp.wxasubaudit(newlist,cid,env)
            print("auditAndRelease-wxasubaudit:",sa)
            if sa['errcode'] == 0: rlt = "小程序‘提审’成功!"
            else:
                isinst = False
                code = c['reserror']
                msg = m['reserror']
                rlt = f"提审失败，原因: {mp.errorcode(sa['errcode'])}"
        elif ts == "ads": #查询小程序提审状态
            gas = mp.getauditstatus(cid,env)
            print("ads-gas:",gas)
            if gas['errcode'] == 0:
                if gas['status'] == 0: rlt = "小程序“审核”成功!"
                elif gas['status'] == 1: 
                    getreason = gas['reason']
                    rlt = getreason.replace('"',"'")
                elif gas['status'] == 2: rlt = "小程序审核中..."
                elif gas['status'] == 3: rlt = "小程序已撤回审核."
                elif gas['status'] == 4: rlt = "小程序审核延后."
            else:
                isinst = False
                code = c['reserror']
                msg = m['reserror']
                rlt = f"查询结果异常，原因: {mp.errorcode(gas['errcode'])}"
        elif ts == "rls":
            wr = mp.wxarelease(cid,env)
            if wr['errcode'] == 0: rlt = "小程序【发布】成功!"
            else: 
                isinst = False
                code = c['reserror']
                msg = m['reserror']
                rlt = f"查询结果异常，原因: {mp.errorcode(gas['errcode'])}"
        elif ts == "ucaudit":
            uda = mp.undocodeaudit(cid,env)
            if uda["errcode"] == 0: rlt = "撤回小程序审核成功!"
            else: 
                isinst = False
                code = c['reserror']
                msg = m['reserror']
                rlt = f"查询结果异常，原因: {mp.errorcode(uda['errcode'])}"
        rltd = {"rlt":rlt}
        print("rltddddddddd:",rltd)
    elif type == "testerAndQrcode":
        isinst = False
        tyb = data['tyb']
        wcid = data['wcid']
        qts = iaq.query_tester_status(cid,wcid)
        rlt = ""
        if tyb == "bindtester":
            bindt = mp.bindtester(wcid,cid,env)
            if bindt["errcode"] == 0:
                rlt = f"体验者【{wcid}】绑定成功! "
                status = 0
                if qts:
                    iaq.update_tester_status(status,qts["id"])
                else:
                    iaq.inst_tester_status(cid,wcid,status)
            else:
                isinst = False
                code = c['reserror']
                msg = m['reserror']
                rlt = f"绑定体验者异常，原因: {mp.errorcode(bindt['errcode'])}"
        elif tyb == "unbindtester":
            unbt = mp.unbindtester(wcid,cid,env)
            if unbt["errcode"] == 0: 
                rlt = f"解绑体验者【{wcid}】成功! "
                status = 1
                if qts:
                    iaq.update_tester_status(status,qts["id"])
                else:
                    iaq.inst_tester_status(cid,wcid,status)
            else:
                isinst = False
                code = c['reserror']
                msg = m['reserror']
                rlt = f"解绑体验者异常，原因: {mp.errorcode(unbt['errcode'])}"
        elif tyb == "getqrcode":
            IMG_SAVE_PATH = os.path.join(settings.BASE_DIR, "static" , "img", "latest_img.jpg")
            qrc = mp.getqrcode(cid,env)
            if not qrc:
                return HttpResponse("图片加载失败", status=400)
            # 确保static目录存在
            os.makedirs(os.path.dirname(IMG_SAVE_PATH), exist_ok=True)
            # 保存图片（新的覆盖旧的）
            with open(IMG_SAVE_PATH, "wb") as f:
                f.write(qrc)
            rlt = "图片获取成功"
                
        rltd = {"rlt":rlt}
        print("rltddddddddd:",rltd)

    if isinst:
        iaq.inst_mprecord(phone,cid,cn,appid,rltd["rlt"],request.session.get('uid'),request.session.get('uname'))
    gr = pdef.get_result(code,msg,rltd)
    return jr(gr)

@never_cache
def queryMiniprogramRecord(request,type):
    data = json.loads(request.body)
    type = data['type']
    code = c['success']
    msg = m['success']
    if type == "querympoc":
        qkey = data['qkey']
        page = data['page']
        num = data['num']
        if page == 1: p=0
        else: p = 10 * (int(page)-1)
        try:
            query_msgData = iaq.query_mprecord(num,p,qkey)
            # print(f"query_msgData: {query_msgData}")
            get_message1 = {}
            x = 0
            for i in query_msgData:
                if str(i["update_time"]) == 'None':
                    t = str(i["create_time"])
                else:
                    t = str(i["update_time"])
                get_message1[x] = {"id":i["id"],"phone":i["phone"],"companyName":i["company_name"],"companyId":str(i["company_id"]),"appId":str(i["app_id"]),"oContent":i["oprate_content"],"uid":i["user_id"],"uname":i["user_name"],"createTime":t}
                x += 1
            gm = list(get_message1.values())
        except Exception as e:
            gm = f"数据库连接异常！{e}"
        # print(pdef.logcss(gct(),"【publicview-other】query_message1:"),gm)
        rltd = {"oprationalInfo":gm}
    elif type == "querytp":
        qkey = data['qkey']
        try:
            totalrlt = iaq.query_mprecord_totalpage(qkey)
            print("totalrlt0000000000:",totalrlt)
            total = str(totalrlt[0]["c"])
        except Exception as e:
            total = "0"
        # print(pdef.logcss(gct(),"【publicview-other】pagecount_total:"),total)
        rltd = {"total":total}
    
    gr = pdef.get_result(code,msg,rltd)
    return jr(gr)

#根据ds查询message
@never_cache
def qmbydsan(request):
    print(' -- [%s] "根据dss查询message"'%pdef.getctime())
    data = json.loads(request.body)
    qdss = data['dss']  # list[int]
    # qnum = data['num']
    get_message = {}
    x = 0
    for qds in qdss:
        kn = dsname[qds]
        cache_key = f'cccache:{kn}'
        mrlt = cache.get(cache_key)
        if mrlt is None:
            with open(cccache, 'r') as infile:
                fdata = json.load(infile)
            mrlt = ast.literal_eval(fdata[kn])
            cache.set(cache_key, mrlt, 3600)
        for i in mrlt:
            cname = i["company_name"]
            cid  = i["company_id"]
            env = i["q_env"]
            ms = i["message"]
            ct = str(i["create_time"])
            ut = str(i["update_time"])
            if ut == 'None':
                t = ct
            else:
                t = ut
            if env == 'prod':
                env = 'P'
            elif env == 'test':
                env = 'T'
            get_message[x] = {"companyName":cname,"companyId":str(cid),"env":env,"message":ms,"t":t}
            x += 1
    gm = list(get_message.values())
    # 按时间倒序
    gm = sorted(gm, key=lambda d: d['t'], reverse=True)
    b = {'qmbydsan':gm}
    code = c['success']
    msg = m['success']
    rlt = pdef.get_result(code,msg,b)
    return jr(rlt)


@never_cache
def aftergetqmbydsan(request): #异步调用query_message_by_dsandnum查询开户企业数据并替换json文件内容
    data = json.loads(request.body)
    qdss = data['dss']  # list[int]
    qnum = data['num']
    updated = False
    for qds in qdss:
        a = iaq.query_message_by_dsandnum([qds], qnum)
        kn = dsname[qds]
        cache_key = f'cccache:{kn}'
        cached_value = cache.get(cache_key)
        if cached_value is None:
            # 缓存过期/未命中：回退到本地文件，避免 None 与查库结果恒不相等导致必然误报
            try:
                with open(cccache, 'r') as infile:
                    fdata = json.load(infile)
                cached_value = ast.literal_eval(fdata[kn])
            except Exception:
                cached_value = []
        # 先比数量，再比 id 序列，任一不同即视为变更
        if bool(a) != bool(cached_value):
            changed = True
        elif a and cached_value:
            if len(a) != len(cached_value):
                changed = True
            else:
                changed = [str(x.get('id')) for x in a] != [str(x.get('id')) for x in cached_value]
        else:
            changed = False
        if changed:
            updated = True
            cache.set(cache_key, a, 3600)
            with open(cccache, 'r') as infile:
                cdata = json.load(infile)
            cdata[kn] = str(a)
            with open(cccache, 'w') as f:
                json.dump(cdata, f, ensure_ascii=False)
    rlt = '更新数据成功！' if updated else '无数据更新！'

    code = c['success']
    msg = m['success']
    gr = pdef.get_result(code,msg,rlt)
    return jr(gr)
