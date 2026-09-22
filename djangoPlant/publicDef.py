from. import random,requests,logger,json,re,hashlib,datetime,random,Counter,current_dir,html,Colors
from django.core.cache import cache  # type: ignore
# from. import Cipher, algorithms, modes,default_backend

HOSTS_URI_test = 'http://msr.jiatuitest.com'  # 测试
HOSTS_URI_prod = 'http://msr.jtscprod.com'  # 生产
fmhis = current_dir / "static/configFile/fmhis.json"

# ── fmhis.json 缓存读写（89MB，避免每次请求都读磁盘）──
_FMHIS_CACHE_KEY = "fmhis:data"
_FMHIS_CACHE_TTL = 3600  # 1小时

def _read_fmhis():
    """读 fmhis.json — Redis 缓存，miss 读文件"""
    data = cache.get(_FMHIS_CACHE_KEY)
    if data is not None:
        return data
    with open(fmhis, 'r') as f:
        data = json.load(f)
    cache.set(_FMHIS_CACHE_KEY, data, _FMHIS_CACHE_TTL)
    return data

def _write_fmhis(data):
    """写 fmhis.json — 自动备份 + 同步更新文件 + 全量缓存 + 计数缓存"""
    from collections import OrderedDict as _OD
    import shutil as _shutil
    # 写前备份（保留最近一份）
    backup = fmhis.with_suffix('.json.bak')
    if fmhis.exists():
        _shutil.copy2(fmhis, backup)
    ordered = _OD()
    if 'ssq_count' in data:
        ordered['ssq_count'] = data['ssq_count']
    for k, v in data.items():
        if k != 'ssq_count':
            ordered[k] = v
    with open(fmhis, 'w') as f:
        json.dump(ordered, f, ensure_ascii=False)
    cache.set(_FMHIS_CACHE_KEY, ordered, _FMHIS_CACHE_TTL)
    if 'ssq_count' in data:
        cache.set('fmhis:ssq_count', data['ssq_count'], _FMHIS_CACHE_TTL)

class publicDef(object):
    def __init__(self):
        self.mergeUser_byHand = "/usercenter/center/user/mergeOfficialUser"  #手工合并用户
        self.setPLC = "/loginservice/card/app/setPartnerVerificationCode"  #设置合伙人固定验证码
        self.login_code_reset="/company-center/company-center/structure/login/code/reset"
        self.sale_add_clue="/ai-referral/flow/saleAddClueInfo" #销售添加线索
        self.del_bind_relationship="/loginservice/gateway/app/cleanExpireCompanyInfo" #清除过期企业信息数据    

    #获取日志文本样式
    def logcss(self, time, desc, type="succ"):
        if type == "succ": color = Colors.BLUE
        elif type == "error": color = Colors.RED
        elif type == "warn": color = Colors.YELLOW
        elif type == "green": color = Colors.GREEN
        rlt = f"{Colors.BOLD}{time}{color} {desc}{Colors.RESET}"
        return rlt
    
    def getctime(self): #实时获取当前时间
        c_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # print("当前时间:", c_time)
        return c_time

    #随机生成字符串
    def randomNum(self,randomlength):
        random_str =''
        base_str ='ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
        length =len(base_str) -1
        for i in range(randomlength):
            random_str +=base_str[random.randint(0, length)]
        return 'HZYGYQWCH'+random_str
    
    #输入的批量数据含有换行、‘,’和空格时，截取生成list（同时存在多种情况，亦可正常截取）
    def split_hh_dh(self,res):
        res = [x for x in re.split(",+|\n+| ",res) if x] 
        # print(self.logcss(self.getctime,'publicDef-批量数据转list: '),res)
        return res
    
    def newname(self,name): #根据现有的字符串，判断最后一位是不是数字，如果是则在最后一位上加1，如果不是则在字符串上加‘1’
        if name[-1:].isdigit():
            nn = name[:-1] + str(int(name[-1:])+1)
        else:
            nn = name + '1'
        return nn

    #根据 word_sep 统计字符串中相同类型词组之和
    def count_char_frequency(text, word_sep=", "):
        # 将文本分割成词组列表
        word_groups = text.split(word_sep)
        # 使用Counter统计每个词组的出现次数
        return Counter(word_groups)

    #手工合并企业用户数据（解决 “企业用户虽然union_id一致，但那是没有合并成功” 的问题）
    def mergeUserByHand(self,companyId,openId,env):
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        mubh = HOSTS_URI + self.mergeUser_byHand
        req_json = {
            "companyId": companyId,
            "openId": openId
        }
        res = requests.post(mubh, json=req_json, timeout=30)
        # print(self.logcss(self.getctime,f'publicDef-【手工合并企业用户】:{mubh}, 入参: {req_json}, 返回数据: {res.json()}'))
        return res.json()
    
    #设置合伙人登录验证码
    def setPantnerLoginCode(self,tel,code,env):
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        geturl = "?code=%s&tel=%s"%(code,tel)
        splc = HOSTS_URI + self.setPLC + geturl
        req_json = ''
        res = requests.post(splc, json=req_json, timeout=30)
        # print(self.logcss(self.getctime,f'publicDef-【设置合伙人登录验证码】:{splc}, 入参: {req_json}, 返回数据: {res.json()}'))
        return res.json()

    #设置销售登录固定验证码
    def salesLoginCodeReset(self,cid,tel,code,env):
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        slcr = HOSTS_URI + self.login_code_reset
        req_json = {
            "companyId":cid,
            "newLoginCode": code,
            "wxBindPhone": tel
        }
        res = requests.post(slcr, json=req_json, timeout=30)
        # print(self.logcss(self.getctime,f'publicDef-【设置销售登录固定验证码】:{slcr}, 入参: {req_json}, 返回数据: {res.json()}'))
        return res.json()

    #销售添加线索
    def saleAddClue(self,companyId,cardId,customName,customMobile,partnerId,env):
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        saci = HOSTS_URI + self.sale_add_clue
        req_json={
            "companyId": companyId,
            "cardId": cardId,
            "customName": customName,
            "customMobile": customMobile,
            "partnerId": partnerId,
            "voucherUrlList": []
        }
        res = requests.post(saci, json=req_json, timeout=30)
        # print(self.logcss(self.getctime,f'publicDef-【销售添加线索】:{saci}, heads:{res.headers}, 入参: {req_json}, 返回数据: {res.json()}'))
        return res.json()

    #清除过期企业信息数据
    def delBindReltionship(self,companyId,env):
        if env == 'prod':
            HOSTS_URI = HOSTS_URI_prod
        elif env == 'test':
            HOSTS_URI = HOSTS_URI_test
        saci = HOSTS_URI + self.del_bind_relationship
        req_json={
            "companyId": companyId
        }
        res = requests.post(saci, json=req_json, timeout=30)
        # print(self.logcss(self.getctime,f'publicDef-【清除过期企业信息数据】:{saci}, heads:{res.headers}, 入参: {req_json}, 返回数据: {res.json()}'))
        return res.json()

    #模块ID转译成文字（O(1) dict 查找）
    _MK_MAP = dict(zip(
        ['M100','M102','M103','M104','M105','M106','M107','M108','M109','M110','M111','M112','M113','M114','M115','M116','M117','M119','M120','M121','M122','M123','M124','M125','M126','M127','M128','M129','M131','M132','M136','M137','M138','M139','M140','M141','M142','M143','M144','M146'],
        ['官网','销售管理组件','推力系统','小程序','动态','推任务','表单','视频','宣传册','案例库','海报','文章','文件','商城','直播','图谱','转介绍2.0','活动分发','优惠券','活码','奥田定制','课程培训','企微助手','红包裂变','聊天侧边栏','云盘版','转介绍3.0','自动化营销','智能渠道码','客户群运营','招商版','推广版(SK)','任务中心(新)','产品库','PLG(企管)','折扣卡','toB版','AI名片','三一重工[定制]','家装版']
    ))

    def mkToName(self, mk):
        return self._MK_MAP.get(mk, mk)

    def md5_encryp(self,s,uid=""):
        md5 = hashlib.md5()     # 创建md5加密对象
        md5.update(str(s).encode('utf-8'))     # 指定需要加密的字符串
        s_md5 = md5.hexdigest()      # 加密后的字符串
        # print('0000:',s_md5)
        if uid == "":
            rlt = s_md5[8:-8]      #截取中间16位
            # arlt = s_md5 + '<br/>' + rlt
            arlt = rlt
        elif uid == '0':
            rlt = s_md5
            arlt = rlt
        else:
            news = uid + s_md5 #md5后在前面拼接userId，做再次加密使用
            # print('0001:',news)
            md5 = hashlib.md5()     # 创建md5加密对象
            md5.update(str(news).encode('utf-8'))     # 指定需要加密的字符串
            s_md5 = md5.hexdigest()      # 加密后的字符串
            arlt = 'MD5-1: ' + news + '<br/>' + 'MD5-2: '+s_md5
            # print('0002:',arlt)
        return arlt

    #hash256加密：将任意长度的数据转换为固定长度的哈希值
    def hash_data(self,data):
        salt = 'gyyqqp'.encode('utf-8')
        # 加盐操作
        salted_pw = str(data) + salt
        hash_object = hashlib.sha256(salted_pw)
        hash_value = hash_object.hexdigest()
        return hash_value

    # #AES 对称加密：使用相同的密钥进行加密和解密
    # def aes_encrypt(self,plaintext):
    #     key = 'ThisIsASecretKeyThisIsASecretKey'  # 密钥，长度必须为16、32字节
    #     k = str(key).encode('utf-8')
    #     pt = str(plaintext).encode('utf-8')
    #     if len(pt) < len(k):
    #         y = (len(k) - len(pt)) * 'Y'
    #         # print('000111')
    #     elif len(pt) > len(k) and len(pt)%len(k) != 0:
    #         y = (len(k) - len(pt)%len(k)) * 'Y'
    #         # print('000222')
    #     else:
    #         y = ''
    #         # print('000333')
    #     backend = default_backend()
    #     cipher = Cipher(algorithms.AES(k), mode=modes.ECB(), backend=backend)
    #     encryptor = cipher.encryptor()
    #     ciphertext = encryptor.update(pt+y.encode('utf-8')) + encryptor.finalize()
    #     return ciphertext.hex() # 输出加密后的密文，以十六进制形式显示
    
    #空字典校验
    def is_not_empty_dict(self,d):
        return all(v for v in d.values()) and all(k for k in d.keys())
    def postRequest(self,hostUri,shortUri,header,reqJson):
        uri = hostUri + shortUri
        req_json=reqJson
        res = requests.post(uri, headers=header, json=req_json, timeout=30)
        # print(self.logcss(self.getctime,f'publicDef-【POST请求接口】:{uri}, heads:{res.headers}, 入参: {req_json}, 返回数据: {res.json()}'))
        return res
    def uploadRequest(self,hostUri,shortUri,header,files,params=None):
        uri = hostUri + shortUri
        res = requests.post(uri, headers=header, files=files, data=params, timeout=60)
        return res
    def getRequest(self,hostUri,shortUri,header,reqParam):
        if reqParam:
            uri = hostUri + shortUri + "?" + reqParam
        else:
            uri = hostUri + shortUri
        res = requests.get(uri, headers=header, timeout=30)
        # print(self.logcss(self.getctime,f'publicDef-【GET请求接口】:{uri}, heads:{res.headers}, 返回数据: {res.json()}'))
        return res

    # 中文获取首字母(第一个文字)
    def single_get_first(self,unicode1):
        str1 = unicode1.encode('gbk')
        try:
            ord(str1)
            return str1
        except:
            asc = str1[0] * 256 + str1[1] - 65536
            if asc >= -20319 and asc <= -20284:return 'a'
            if asc >= -20283 and asc <= -19776:return 'b'
            if asc >= -19775 and asc <= -19219:return 'c'
            if asc >= -19218 and asc <= -18711:return 'd'
            if asc >= -18710 and asc <= -18527:return 'e'
            if asc >= -18526 and asc <= -18240:return 'f'
            if asc >= -18239 and asc <= -17923:return 'g'
            if asc >= -17922 and asc <= -17418:return 'h'
            if asc >= -17417 and asc <= -16475:return 'j'
            if asc >= -16474 and asc <= -16213:return 'k'
            if asc >= -16212 and asc <= -15641:return 'l'
            if asc >= -15640 and asc <= -15166:return 'm'
            if asc >= -15165 and asc <= -14923:return 'n'
            if asc >= -14922 and asc <= -14915:return 'o'
            if asc >= -14914 and asc <= -14631:return 'p'
            if asc >= -14630 and asc <= -14150:return 'q'
            if asc >= -14149 and asc <= -14091:return 'r'
            if asc >= -14090 and asc <= -13119:return 's'
            if asc >= -13118 and asc <= -12839:return 't'
            if asc >= -12838 and asc <= -12557:return 'w'
            if asc >= -12556 and asc <= -11848:return 'x'
            if asc >= -11847 and asc <= -11056:return 'y'
            if asc >= -11055 and asc <= -10247:return 'z'
            return ''
    #提取汉字首字母
    def getFirstLetter(self,string):
        for ch in string:
            if '\u4e00' <= ch <= '\u9fff':
                lst = list(string)
                charLst = []
                for l in lst:
                    charLst.append(self.single_get_first(l))
                return ''.join(charLst)
        return False

    """def resolve_domain(self,domain):
        #解析域名，返回IP地址列表
        ip_list = []
        try:
            # 解析域名，返回一个IP地址列表
            addrs = socket.getaddrinfo(domain, None)
            addr = addrs[0]
            ip = addr[4][0]
            if ip == '172.18.18.45':
                ips = ' msr&eureka: 华为云 '
                a = 2
            ip_list.append(ips)
        except Exception as e:
            print(self.getctime(),e)
        return ip_list[0],a
    """


    def contains_only_chinese(self,input_string): #纯汉字校验
        pattern = re.compile(r'[\u4e00-\u9fa5]+')
        match = pattern.fullmatch(input_string)
        return match is not None
    def contains_only_letters(self,input_string): #纯字母校验
        return input_string.isalpha()
    
    def get_result(self, code, msg="", data=""):
        grlt = {"code":code, "msg":msg, "data":data}
        # print(self.logcss(self.getctime(),"【publicDef-get_result】"),f"get_result:{grlt}")
        return grlt
    def get_sorting_key(self,item):
        return item['ct']

    def getJsonInfo(self,jsonfile):
        with open(jsonfile, 'r') as infile:
            data = json.load(infile)
        return data
    def writeIntoJson(self,jsonfile,data):
        try:
            with open(jsonfile, 'w') as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            print(self.logcss(self.getctime,f'【publicDef-writeIntoJson】','error'),f'写入json失败,{e}')

    #去除转义符
    def process_latex_text(self,text):
        # 1. 去除多余的反斜杠（保留合法的 LaTeX 命令）
        clean_text = re.sub(r'\\(?![a-zA-Z]+|{|})', '', text)
        # 2. 处理 HTML 转义字符
        clean_text = html.unescape(clean_text)
        return clean_text

    def extract_prefix_and_number(self, account): #分离账号的前缀和数字部分，兼容邮箱格式，保留前导零位数
        # 先提取域名后缀（如 @jt.com）
        match_domain = re.search(r'(@[\w.]+)$', account)
        domain_suffix = match_domain.group(1) if match_domain else ''
        # 去掉后缀后的主体部分
        main_part = account[:match_domain.start()] if match_domain else account
        # 正则匹配：从末尾往前取连续数字，其余为前缀
        match = re.match(r'^(.+?)(\d+)$', main_part)
        if not match:
            prefix = main_part
            number = 0
            width = 0
        else:
            prefix = match.group(1)  # 前缀（如 qq / qq123a）
            raw_num = match.group(2)  # 原始数字字符串（如 '001'）
            number = int(raw_num)
            width = len(raw_num)  # 位数，用于前导零补全（如 3）
        return prefix, number, domain_suffix, width

class fivemillion(object):
    def saveSSQ(self,try_nums,isl='no'):
        print(f"生成中...")
        self._lottery_migrate_from_json()
        if isl == 'no':
            ssqra = self.SSQ(try_nums)
            self._lottery_insert_batch('ssq', ssqra)
            return ssqra
        elif isl == 'yes':
            total = self._lottery_count('ssq')
            if total == 0:
                return ['无数据！']
            if try_nums > total:
                return [f'本地数据的总和为{total}, 请填写小于等于该数值的次数!']
            return self._lottery_random_sample('ssq', try_nums)
    def _lottery_count(self, ltype='ssq'):
        from django.db import connection
        with connection.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM lottery_records WHERE ltype=%s", [ltype])
            return cur.fetchone()[0]

    def _lottery_insert_batch(self, ltype, numbers_list):
        """批量写入抽奖记录（事务保证原子性），完成后日志打印结果"""
        from django.db import connection, transaction
        import time as _time
        total = len(numbers_list)
        t0 = _time.time()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rows = [(ltype, str(n), now) for n in numbers_list]
        # 获取当前计数（优先 Redis，未命中才 COUNT）
        cached = cache.get('fmhis:ssq_count')
        old_count = cached if cached is not None else self._lottery_count(ltype)
        try:
            with transaction.atomic():
                with connection.cursor() as cur:
                    cur.executemany(
                        "INSERT INTO lottery_records (ltype, numbers, create_time) VALUES (%s, %s, %s)",
                        rows
                    )
            elapsed = _time.time() - t0
            cache.set('fmhis:ssq_count', old_count + total, timeout=None)
            print(f"[抽奖入库] {ltype} | {total} 条 | 全部成功 | 耗时 {elapsed:.1f}s")
        except Exception as e:
            elapsed = _time.time() - t0
            print(f"[抽奖入库] {ltype} | {total} 条 | 失败 {str(e)[:200]} | 耗时 {elapsed:.1f}s")

    def _lottery_random_sample(self, ltype, count):
        """从 SQLite 随机取 count 条记录（高效：先 count → 随机 offset → 批量取）"""
        from django.db import connection
        total = self._lottery_count(ltype)
        if total == 0:
            return []
        import random as _rand
        sample_count = min(count, total)
        offsets = sorted(_rand.sample(range(total), sample_count))
        results = []
        with connection.cursor() as cur:
            for offset in offsets:
                cur.execute(
                    "SELECT numbers FROM lottery_records WHERE ltype=%s LIMIT 1 OFFSET %s",
                    [ltype, offset]
                )
                row = cur.fetchone()
                if row:
                    results.append(row[0])
        return results

    def _lottery_clear_all(self, ltype=None):
        """硬删除抽奖记录"""
        from django.db import connection
        with connection.cursor() as cur:
            if ltype:
                cur.execute("DELETE FROM lottery_records WHERE ltype=%s", [ltype])
            else:
                cur.execute("DELETE FROM lottery_records")
        cache.set('fmhis:ssq_count', self._lottery_count(ltype), timeout=None)

    def _lottery_migrate_from_json(self):
        """首次启动：将 fmhis.json 旧数据迁移到 SQLite（后台异步）"""
        if not fmhis.exists():
            return

        # 只迁移一次（通过文件重命名判断）
        if fmhis.with_suffix('.json').name.endswith('.migrated'):
            return

        import threading
        def _migrate():
            from django.db import connection
            try:
                with open(fmhis, 'r') as f:
                    old = json.load(f)
                ssq_list = old.get('ssq', [])
                if not ssq_list:
                    return
                total = len(ssq_list)
                t0 = __import__('time').time()
                print(f"{Colors.BOLD}{Colors.YELLOW}[迁移] fmhis.json → SQLite: {total} 条…{Colors.RESET}")
                ok = 0
                failed = 0
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with connection.cursor() as cur:
                    for i, n in enumerate(ssq_list):
                        try:
                            cur.execute(
                                "INSERT INTO lottery_records (ltype, numbers, create_time) VALUES (%s, %s, %s)",
                                ['ssq', str(n), now],
                            )
                            ok += 1
                        except Exception:
                            failed += 1
                        if (i + 1) % 100000 == 0:
                            print(f"  … {i+1}/{total} (+{__import__('time').time()-t0:.0f}s)")
                fmhis.rename(fmhis.with_suffix('.json.migrated'))
                cache.set('fmhis:ssq_count', self._lottery_count('ssq'), timeout=None)
                elapsed = __import__('time').time() - t0
                msg = f"[迁移] 完成 | 总 {total} 条 | 成功 {ok} 条"
                if failed:
                    msg += f" | 失败 {failed} 条"
                msg += f" | 耗时 {elapsed:.1f}s"
                print(f"{Colors.BOLD}{Colors.GREEN}{msg}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.BOLD}{Colors.RED}[迁移] 失败: {e}{Colors.RESET}")
        threading.Thread(target=_migrate, daemon=True).start()

    def __init__(self):
        self.getcpinfo = "https://api.tanshuapi.com/api/caipiao/v1/query?key=bf4ffd6d67a555a62db7dc8a7c75aa02&"

    def format_li(self, red_num_li, blue_num_li, type):
        """格式化列表，美观显示列表"""
        def _fmt(num):
            return f'0{num}' if num < 10 else str(num)

        # 安全转换，不修改原始列表
        reds = [_fmt(i) for i in red_num_li]
        blues = [_fmt(i) for i in blue_num_li]

        if type == 'ssq':
            rlt = f'{reds[0]},{reds[1]},{reds[2]},{reds[3]},{reds[4]},{reds[5]} — {blues[0]}'
            srlt = rlt
        elif type == 'dlt':
            rlt = '{},{},{},{},{} — {},{}'.format(reds[0], reds[1], reds[2], reds[3], reds[4],
                                                  blues[0], blues[1])
            srlt = rlt
        return rlt

    # SSQ 红1~33  蓝1~16  （二、四、日）
    # DLT 红1~35  蓝1~12  （一、三、六）
    def SSQ(self, try_nums):
        """SSQ随机选号"""
        red_num_li = []
        blue_num_li = []
        ssqra = []
        for i in range(try_nums):
            red_num_li.clear()
            blue_num_li.clear()
            while len(red_num_li) <= 5:
                temp_r_num = random.randint(1, 33)
                if temp_r_num not in red_num_li:
                    red_num_li.append(temp_r_num)
            temp_b_num = random.randint(1, 16)
            blue_num_li.append(temp_b_num)
            red_num_li.sort()  # 从小到大排序
            # print('ssq--red_num_li, blue_num_li:',red_num_li, blue_num_li)
            ssqr = self.format_li(red_num_li, blue_num_li, 'ssq')
            ssqra.append(ssqr)
            # ssq-rlt 日志仅在总量 ≤10 时打印（避免大批量生成时 stdout I/O 拖慢）
        print(f"生成完成，共{try_nums}条。")
        return ssqra
    
    # ── Lottery SQLite helpers ──

    def DLT(self, try_nums):
        """大乐透随机选号"""
        red_num_li = []
        blue_num_li = []
        dltra = []
        for i in range(try_nums):
            red_num_li.clear()
            blue_num_li.clear()
            while len(red_num_li) <= 4:
                temp_r_num = random.randint(1, 35)
                if temp_r_num not in red_num_li:
                    red_num_li.append(temp_r_num)
            while len(blue_num_li) <= 1:
                temp_b_num = random.randint(1, 12)
                if temp_b_num not in blue_num_li:
                    blue_num_li.append(temp_b_num)
            red_num_li.sort()
            blue_num_li.sort()
            # print('dlt--red_num_li, blue_num_li:',red_num_li, blue_num_li)
            dltr = self.format_li(red_num_li, blue_num_li, 'dlt')
            dltra.append(dltr)
        # print('dltra:',dltra)
        return dltra

    def happy8(self,x,y):
        j = 0
        b = []
        while j < y:
            a = []
            i = 0
            while i < x:
                num = random.randint(1, 80) #随机生成1-80之间的整数
                if num in a:
                    pass
                else:
                    a.append(num)
                    i += 1
                a.sort(key=None, reverse=False) #数字从小到大排序
            a = [str(x) for x in a] #将a中的int转化为str
            a = ','.join(a) #将a从list转为str
            b.append(a)
            j += 1
        return b

    def getCpNumberInfo(self,issueno="",caipiaoid=11):
        uri = self.getcpinfo + f"caipiaoid={caipiaoid}&issueno={issueno}"
        req_json=""
        # print("getCpNumberInfo:",uri,req_json)
        try:
            res = requests.get(uri, json=req_json,verify=False, timeout=30)
            # print(publicDef().logcss(publicDef().getctime(),f'【publicDef-saveSSQ】'),f'【获取ssq中奖信息】:{uri}, 入参: {req_json},heads:{res.headers}, 返回数据: {res.json()}')
            return res.json()
        except Exception as e:
            print("getCpNumberInfo error:",e)

