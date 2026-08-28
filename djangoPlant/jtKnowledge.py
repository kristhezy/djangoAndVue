from.DeleteInterface import DeleteInterface,pdef
from.QueryInterface import QueryInterface
from. import current_dir

di = DeleteInterface()
qi = QueryInterface()
grayci = current_dir / "static/configFile/grayCI.txt"

def gct():
    return pdef.getctime()

class jtKnowledge(object):
    def __init__(self):
        pass

    def delchecked(self,companyId,userId,env,delcheck,ppc=""):
        if delcheck == 'delclue':
            dcu = di.del_clueUser(companyId,userId,env)
            print('dcu:',dcu)
            if dcu['code'] == 0 and dcu['msg'] == '成功':
                rlt = '访客/线索【%s】删除成功！'%userId
            else:
                rlt = '访客/线索【%s】删除失败, 原因是: %s'%(userId,dcu['msg']+', '+dcu['data'])
            print(f"jtKnowledge-delchecked: {rlt}")
        elif delcheck == 'delpartner':
            if ppc:
                dpi = di.clean_partnerAppletInfo(companyId,userId,ppc,env)
                # print('dpi:',dpi)
                if dpi['code'] == 0 and dpi['msg'] == '成功':
                    rlt = '合伙人(%s)删除成功！'%ppc
                else:
                    delpi = di.del_partnerInfo(companyId,userId,ppc,env)
                    if delpi['code'] == 0:
                        rlt = '合伙人(%s)删除成功！'%ppc
                    else:
                        rlt = '合伙人(%s)删除失败, 原因是: %s'%(ppc,dpi['msg'])
            else:
                rlt = '"合伙人ID"不能为空！'
        # print('44444444',rlts)
        return str(rlt)
    #查询灰度企业
    def queryGCI(self):
        try:
            qgc = qi.query_grayCompany(env='prod')
            cidIzone = qgc["propertySources"][0]["source"]["gwzuul.companyIdToIzoneStr"]
            cidsSplit = cidIzone[:-2].split(',')
            # print('cidsSplit:',cidsSplit)
            cids = []
            g = {}
            env = 'prod'
            for x in cidsSplit:
                # print('xxxxxxxx:',x)
                if '#' not in x:
                    c = "".join(list(filter(str.isdigit, x)))
                    # print('cccccccc:',c)
                    if len(c) >=18 :
                        cids.append(c)
            print(pdef.logcss(gct(),'【jtKnowledge-queryGCI】'),'cids:',cids)
            if cids == []:
                g = {""}
            else:
                for cid in cids:
                    f = qi.query_companyInfo(cid,env)
                    if f['data']:
                        cn = f['data']['companyName']
                        # print(cn,type(cn))
                        g[cid] = str(cn)
            g = str(g)
            print(pdef.logcss(gct(),'【jtKnowledge-queryGCI】'),'灰度企业信息:',g)
        except Exception as error:
            print(pdef.logcss(gct(),'【jtKnowledge-queryGCI】'),'更新灰度企业数据接口失败!',error)
        else:
            with open(grayci,"r",encoding='utf-8') as f:
                gci = f.readline()
            if gci != g:
                with open(grayci,"w",encoding='utf-8') as f:
                    f.write(g)
                rlt = '更新灰度企业数据成功！'
            else:
                rlt = '已是最新数据！'
            return rlt
