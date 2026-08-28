# -*- coding: utf-8 -*-
# @Time    : 2021/9/6 19:50
# @Author  : krist
# @File    : common.py
import urllib3
from time import strftime, localtime
from. import requests,re,json,logger,time
from.publicDef import publicDef

pdef = publicDef()

urllib3.disable_warnings()
def show_distance_time(func):
    def wrapper(*args):
        t1 = time()
        res = func(*args)
        t2 = time()
        # print(func.__name__, "runtime：", t2 - t1)
        return res
    return wrapper


class GetCode:

    @show_distance_time
    def verification_code(self, env, ph_num, end_time=10):
        """
        获取手机验证码
        """

        kibana_sc_url = 'http://kibana-log.jiatuiyun.net/elasticsearch/_msearch'
        # kibana_sc_url = 'http://172.21.8.3:5601/internal/bsearch?compress=true'
        kibana_test_url = 'http://dev-kibana-log.jiatuiyun.net/elasticsearch/_msearch'
        phone_num = ph_num
        t0 = time()
        # t1查询开始时间，10代表10分钟
        t1 = int(round(t0 * 1000)) - (end_time * 60000)
        t2 = int(round(t0 * 1000))
        dt = strftime("%Y-%m-%d %H:%M:%S", localtime(t1 // 1000))
        dt2 = strftime("%Y-%m-%d %H:%M:%S", localtime(t2 // 1000))
        print(f'<查询日志时间范围：{dt} ~ {dt2}>')
        if env == 'test':
            kibana_url = kibana_test_url
            data3 = '{"index":"ap*","ignore_unavailable":true,"timeout":30000,"preference":1684224283890}\n'\
                '{"version":true,"size":500,"sort":[{"find_time":{"order":"desc","unmapped_type":"boolean"}}],'\
                '"_source":{"excludes":[]},"aggs":{"2":{"date_histogram":{"field":"find_time","interval":"30s",'\
                '"time_zone":"Asia/Shanghai","min_doc_count":1}}},"stored_fields":["*"],"script_fields":{},'\
                '"docvalue_fields":["@timestamp","find_time"],"query":{"bool":{"must":[{"query_string":{"query":"param","analyze_wildcard":true,"default_field":"*"}},'\
                '{"match_phrase":{"message":{"query":"%s"}}},{"range":{"find_time":{"gte":%s,"lte":%s,"format":"epoch_millis"}}}],'\
                '"filter":[],"should":[],"must_not":[]}},"highlight":{"pre_tags":["@kibana-highlighted-field@"],'\
                '"post_tags":["@/kibana-highlighted-field@"],"fields":{"*":{}},"fragment_size":2147483647}}\n' % (phone_num, t1, t2)
        elif env == 'prod':
            kibana_url = kibana_sc_url
            data3 = '{"batch":[{"request":{"id":"FjIyZm5saGpkUi1XT3ZLVGJrUjZ3cFEfMUdPb1ZZTjJUYk9QcGJJbF8tNWRZQToxOTkwMjcxMw==",'\
                '"params":{"index":"app*","body":{"sort":[{"@timestamp":{"order":"desc","unmapped_type":"boolean"}}],'\
                '"fields":[{"field":"*","include_unmapped":"true"},{"field":"@timestamp","format":"strict_date_optional_time"}],'\
                '"size":500,"version":true,"script_fields":{},"stored_fields":["*"],"runtime_mappings":{},"_source":false,'\
                '"query":{"bool":{"must":[],"filter":[{"multi_match":{"type":"best_fields","query":"param","lenient":true}},'\
                '{"range":{"@timestamp":{"format":"strict_date_optional_time","gte":%s,"lte":%s}}},'\
                '{"match_phrase":{"appname":"oa-service"}},{"match_phrase":{"message":%s}}],"should":[],"must_not":[]}},'\
                '"highlight":{"pre_tags":["@kibana-highlighted-field@"],"post_tags":["@/kibana-highlighted-field@"],'\
                '"fields":{"*":{}},"fragment_size":2147483647}},"track_total_hits":false,"preference":1693386397285}},'\
                '"options":{"strategy":"ese","isSearchStored":false,"executionContext":{"type":"application","name":"discover",'\
                '"url":"/app/discover","page":"app","id":"new","description":"fetch documents"}}}]}' %(phone_num, t1, t2)
        
        # data2 = '{"index":"ap*","ignore_unavailable":true,"timeout":30000,"preference":1684224283890}\n'\
        #         '{"version":true,"size":500,"sort":[{"find_time":{"order":"desc","unmapped_type":"boolean"}}],'\
        #         '"_source":{"excludes":[]},"aggs":{"2":{"date_histogram":{"field":"find_time","interval":"30s",'\
        #         '"time_zone":"Asia/Shanghai","min_doc_count":1}}},"stored_fields":["*"],"script_fields":{},'\
        #         '"docvalue_fields":["@timestamp","find_time"],"query":{"bool":{"must":[{"query_string":{"query":"param","analyze_wildcard":true,"default_field":"*"}},'\
        #         '{"match_phrase":{"message":{"query":"%s"}}},{"range":{"find_time":{"gte":%s,"lte":%s,"format":"epoch_millis"}}}],'\
        #         '"filter":[],"should":[],"must_not":[]}},"highlight":{"pre_tags":["@kibana-highlighted-field@"],'\
        #         '"post_tags":["@/kibana-highlighted-field@"],"fields":{"*":{}},"fragment_size":2147483647}}\n' % (phone_num, t1, t2)
        data3 = '{"index":"ap*","ignore_unavailable":true,"timeout":30000,"preference":1684224283890}\n'\
                '{"version":true,"size":500,"sort":[{"find_time":{"order":"desc","unmapped_type":"boolean"}}],'\
                '"_source":{"excludes":[]},"aggs":{"2":{"date_histogram":{"field":"find_time","interval":"30s",'\
                '"time_zone":"Asia/Shanghai","min_doc_count":1}}},"stored_fields":["*"],"script_fields":{},'\
                '"docvalue_fields":["@timestamp","find_time"],"query":{"bool":{"must":[{"query_string":{"query":"param","analyze_wildcard":true,"default_field":"*"}},'\
                '{"match_phrase":{"message":{"query":"%s"}}},{"range":{"find_time":{"gte":%s,"lte":%s,"format":"epoch_millis"}}}],'\
                '"filter":[],"should":[],"must_not":[]}},"highlight":{"pre_tags":["@kibana-highlighted-field@"],'\
                '"post_tags":["@/kibana-highlighted-field@"],"fields":{"*":{}},"fragment_size":2147483647}}\n' % (phone_num, t1, t2)
        headers = {
            "kbn-version": "6.3.2",
            "user-agent": "py",
            "content-type": "application/x-ndjson"
        }
        response = requests.post(kibana_url, data=data3, headers=headers, verify=False)
        # print('【响应结果】: ',type(response),response.status_code)
        rsp = json.loads(response.text)
        # print('【接口返回数据】: ',rsp)
        if response.status_code == 200:
            try:
                hits = rsp['responses'][0]['hits']['hits']
                hitslen = len(hits)
                print('111111111',hitslen,hits)
                print('%s 【查询短信hits段】 hits内容: %s, hits长度: %s' %(pdef.getctime(),hits,hitslen))
                if hitslen == 0:
                    tc = '近10分钟无当前号码的短信验证码！'
                else:
                    x = '当前操作验证码：'
                    y = "param='["
                    i = 0
                    while i < hitslen:
                        # print('333333333333333',hits[i]['_source'])
                        if x in hits[i]['_source']['message'] or y in hits[i]['_source']['message']:
                            r = hits[i]['_source']['message']
                            print('%s 【查询短信message】: %s' %(pdef.getctime(),r))
                            break
                        i += 1
                    if r:
                        if x in r:
                        # code2 = re.findall('content .*?。 ', r)
                            code2 = re.findall(r"content='([^']+)'",r)
                            print(code2)
                            c = code2[0].split("，")[0]
                            print(c[8:])
                            tc = c[8:]
                        if y in r:
                            code = re.findall(r"param='([^']+)'",r)
                            print('code',code)
                            # print('333333',type(r))
                            tc = code[0][1:-1]
                    else:
                        tc='近10分钟无当前号码的短信验证码！'
                print('tc',tc)
                return tc
            except IndexError as e:
                return f'该时间段未找到验证码, 报错：{e}'
        else:
            return f'接口异常：{response}'

