from.ov_setting import OVSetting,pdef
from.pub_InputAndQuery import InputAndQuery
from.QueryInterface import QueryInterface
ovs = OVSetting()
iaq = InputAndQuery()
qi = QueryInterface()

def gct():
    return pdef.getctime()

#originview操作记录入库
def ov_opretor_records_instdb(companyId,cname,env,uid,uname,rlt,msr,ds,sver):
    if cname:
        cname = cname
    else:
        if int(sver) == 6:
            qci_rlt = None
        else:
            try:
                qci_rlt = ovs.query_company_info(companyId, env, sver) #调用查询企业信息接口
            except:
                qci_rlt = None
        if not qci_rlt or qci_rlt == 'null':
            cn = iaq.query_cnbycid(companyId,env)
            print(f"ov_opretor_records_instdb-cn: {cn}")
            if len(cn) == 0:
                cname = '/'
            else:
                cname = cn['company_name']
        elif qci_rlt['data'] == None:
            cname = '/'
        else:
            cname = qci_rlt['data']['companyName']
    iaq.inst_data(uid,uname,env,companyId,cname,rlt,int(ds),int(msr),int(sver))
#saasview操作记录入库
def sv_opretor_records_instdb(companyId,env,uid,uname,rlt,ds,msr,companyName="",svers=1):
    if companyName:
        cname = companyName
    else:
        if int(svers) == 1:
            try:
                qci_rlt = qi.query_companyInfo(companyId, env) #调用saas查询企业信息接口
            except:
                qci_rlt = 'null'
            if qci_rlt == 'null':
                cn = iaq.query_cnbycid(companyId,env)
                if len(cn) == 0:
                    cname = '企业已冻结或已注销'
                else:
                    cname = cn.get("company_name", "/")
            elif qci_rlt['data'] == None:
                cname = '/'
            else:
                cname = qci_rlt['data']['companyName']
            print(pdef.logcss(gct(),"【pub_utils-sv_opretor_records_instdb】"),"SAAS company name:",cname)
        elif int(svers) == 3:
            try:
                qci_rlt = ovs.query_company_info(companyId, env, svers) #调用查询企业信息接口
            except:
                qci_rlt = None
            if not qci_rlt or qci_rlt == 'null':
                cn = iaq.query_cnbycid(companyId,env)
                if len(cn) == 0:
                    cname = '/'
                else:
                    cname = cn.get("company_name", "/")
            elif qci_rlt['data'] == None:
                cname = '/'
            else:
                cname = qci_rlt['data']['companyName']
            print(pdef.logcss(gct(),"【pub_utils-sv_opretor_records_instdb】"),"origin company name:",cname)
        else:
            cname = "/"
    iaq.inst_data(uid,uname,env,companyId,cname,rlt,int(ds),int(msr),svers)

# utils.py（可放在任意app下，比如users/utils.py）
from django.contrib.auth import authenticate, login as django_login #type: ignore
from django.utils import timezone #type: ignore
from django.db import connection #type: ignore
from django.contrib.auth.models import User #type: ignore

# 注册新用户（替换你原有注册逻辑）
def create_user_with_beijing_time(username,name,email,password,isActive,isStaff):
    user = User.objects.create_user(
        username=username,
        last_name=name,
        email=email,
        password=password,  # 密码哈希
        is_active=isActive,
        is_staff=isStaff
    )
    # 2. 核心修正：通过原生SQL将date_joined+8小时
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE auth_user 
            SET date_joined = datetime(date_joined, '+8 hours') 
            WHERE id = %s;
        """, [user.id])
    return user

def login_with_beijing_time(request, username, password):
    # 1. 原有认证逻辑
    user = authenticate(request, username=username, password=password)
    print("login_with_beijing_time-user: ",user)
    if not user:
        return None  # 认证失败
    
    # 2. 执行Django内置login（会自动更新last_login为UTC时间）
    django_login(request, user)
    
    # 3. 手动修正last_login为北京时间（核心：+8小时）
    beijing_time = timezone.localtime()  # 带时区的当前北京时间
    with connection.cursor() as cursor:
        # 仅更新last_login字段为北京时间，无需写复杂SQL
        cursor.execute("""
            UPDATE auth_user 
            SET last_login = %s 
            WHERE id = %s;
        """, [beijing_time, user.id])  # 参数化查询，安全无注入
        connection.commit()
    return user  # 返回认证后的用户对象