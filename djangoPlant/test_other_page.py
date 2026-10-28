"""「操作变更记录」页（/pv/other 系列接口）回归测试。

覆盖三项修复：
1. pagecount / other_part 必须登录后才能访问（原本漏了 @login_required）
2. 删除结果用 ok 字段明确成败，且不再把异常原文返回给前端
3. 分页 offset 按请求传入的 num 计算（原本把 10 写死）
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.cache import cache  # type: ignore
from django.db import connection  # type: ignore
from unittest import mock
from datetime import datetime
import json

from djangoPlant import publicview
from djangoPlant.pub_InputAndQuery import InputAndQuery
from mysqlite.models import QGetMessage

BASE = {'page': 1, 'env': '', 'vers': '', 'num': 10,
        'compid': '', 'compname': '', 'uname': '', 'minfo': ''}


def _post(payload):
    return dict(data=json.dumps(payload), content_type='application/json')


def login_client():
    """已登录的测试客户端。

    SessionExpiryMiddleware 要求 session 里有 isLoggedIn，
    MenuPermissionMiddleware 要求 session['menus'] 含 'other'（/pv/other 是受控菜单）。
    """
    c = Client()
    c.force_login(User.objects.create_user('othertest', password='x'))
    s = c.session
    s['isLoggedIn'] = True
    s['menus'] = ['other']
    s.save()
    return c


class LoginRequiredTests(TestCase):
    """修复 1：接口必须登录"""

    def test_pagecount_requires_login(self):
        resp = Client().post('/pv/pagecount', **_post(BASE))
        self.assertIn(resp.status_code, (302, 403))

    def test_delmsg_requires_login(self):
        resp = Client().post('/pv/other/delmsg', **_post({'id': 1}))
        self.assertIn(resp.status_code, (302, 403))

    def test_queryOpraterName_requires_login(self):
        resp = Client().post('/pv/other/queryOpraterName', **_post({}))
        self.assertIn(resp.status_code, (302, 403))

    def test_pagecount_ok_after_login(self):
        resp = login_client().post('/pv/pagecount', **_post(BASE))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('total', resp.json()['data'])

    def test_other_still_ok_after_login(self):
        """对照：原本就有 @login_required 的 /pv/other 行为不变"""
        with mock.patch.object(publicview.iaq, 'query_message1', return_value=[]):
            resp = login_client().post('/pv/other', **_post(BASE))
        self.assertEqual(resp.status_code, 200)


class PaginationOffsetTests(TestCase):
    """修复 3：offset = num * (page - 1)，不再是写死的 10"""

    def _offset_for(self, num, page):
        with mock.patch.object(publicview.iaq, 'query_message1', return_value=[]) as m:
            login_client().post('/pv/other', **_post({**BASE, 'num': num, 'page': page}))
        return m.call_args[0]

    def test_offset_follows_num(self):
        """num=20 第 3 页：offset 应为 40（旧实现会给 20，导致与第 2 页重叠）"""
        args = self._offset_for(20, 3)
        self.assertEqual(args[0], 20)
        self.assertEqual(args[1], 40)

    def test_num_10_behaviour_unchanged(self):
        """默认 num=10 时结果与修复前一致，保证不回归"""
        args = self._offset_for(10, 3)
        self.assertEqual(args[0], 10)
        self.assertEqual(args[1], 20)

    def test_first_page_offset_zero(self):
        args = self._offset_for(20, 1)
        self.assertEqual(args[1], 0)

    def test_invalid_params_fall_back(self):
        """非法 num/page 回落为 10 / 1，不再抛 500"""
        args = self._offset_for('abc', 'xyz')
        self.assertEqual(args[0], 10)
        self.assertEqual(args[1], 0)

    def test_negative_params_clamped(self):
        args = self._offset_for(-5, 0)
        self.assertEqual(args[0], 10)
        self.assertEqual(args[1], 0)


class DeleteResultTests(TestCase):
    """修复 2：删除成败用 ok 明确区分"""

    def _del(self, rv=None, side_effect=None):
        kw = {'return_value': rv} if side_effect is None else {'side_effect': side_effect}
        with mock.patch.object(publicview.iaq, 'del_message', **kw):
            resp = login_client().post('/pv/other/delmsg', **_post({'id': 1}))
        return resp.json()['data']

    def test_success_returns_ok_true(self):
        d = self._del(rv=1)
        self.assertTrue(d['ok'])
        self.assertEqual(d['otherPartRlt'], '删除成功！')

    def test_missing_record_returns_ok_false(self):
        """记录不存在/已删除时不能再伪装成成功"""
        d = self._del(rv=0)
        self.assertFalse(d['ok'])
        self.assertNotEqual(d['otherPartRlt'], '删除成功！')

    def test_exception_returns_ok_false(self):
        d = self._del(side_effect=Exception('connection to server was lost'))
        self.assertFalse(d['ok'])

    def test_exception_detail_not_leaked(self):
        """异常原文不得出现在响应里（旧实现直接把 str(e) 返回前端）"""
        d = self._del(side_effect=Exception('SQL syntax error near secret_table'))
        self.assertNotIn('secret_table', d['otherPartRlt'])
        self.assertNotIn('SQL syntax error', d['otherPartRlt'])


def _row(q_env):
    return {'id': 1, 'q_env': q_env, 'company_name': 'c', 'company_id': '1',
            'message': 'm', 'uname': 'u', 'create_time': '2026-01-01 00:00:00',
            'update_time': 'None', 'server_side': None, 'version': None}


class EnvLabelTests(TestCase):
    """修复 4：env 展示名不再互相污染"""

    def _call(self, rows):
        with mock.patch.object(publicview.iaq, 'query_message1', return_value=rows):
            resp = login_client().post('/pv/other', **_post(BASE))
        return resp.json()['data']['oprationalInfo']

    def test_known_env_mapped(self):
        rows = self._call([_row('prod'), _row('test'), _row('nxlt')])
        self.assertEqual([r['env'] for r in rows], ['生产', '测试', '宁夏联通'])

    def test_unknown_env_does_not_leak_previous_row(self):
        """旧实现复用了筛选变量 env 且 if/elif 没有 else：
        未知环境值会沿用上一条记录的中文名，显示为「生产」。"""
        rows = self._call([_row('prod'), _row('weird-env')])
        self.assertEqual(rows[0]['env'], '生产')
        self.assertEqual(rows[1]['env'], 'weird-env')


class PagecountTests(TestCase):
    """修复 5：pagecount 去掉死代码"""

    def test_returns_real_count(self):
        with mock.patch.object(publicview.iaq, 'query_message_total', return_value={'c': 42}):
            resp = login_client().post('/pv/pagecount', **_post(BASE))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['data']['total'], '42')

    def test_no_longer_reads_config_file(self):
        """旧实现先 open(CCCache.json)，文件缺失/损坏会 500，挡住后面有效的查询。
        现在整个请求链路不应再读任何文件。"""
        with mock.patch.object(publicview.iaq, 'query_message_total', return_value={'c': 7}), \
             mock.patch('builtins.open', side_effect=AssertionError('不应再读文件')):
            resp = login_client().post('/pv/pagecount', **_post(BASE))
        self.assertEqual(resp.json()['data']['total'], '7')


class OtherErrorTests(TestCase):
    """修复 6：查询失败不再伪装成成功"""

    def test_exception_returns_ok_false(self):
        with mock.patch.object(publicview.iaq, 'query_message1',
                               side_effect=Exception('db down secret_table')):
            resp = login_client().post('/pv/other', **_post(BASE))
        d = resp.json()['data']
        self.assertFalse(d['ok'])
        self.assertEqual(d['oprationalInfo'], [])

    def test_exception_detail_not_leaked(self):
        with mock.patch.object(publicview.iaq, 'query_message1',
                               side_effect=Exception('db down secret_table')):
            resp = login_client().post('/pv/other', **_post(BASE))
        self.assertNotIn('secret_table', json.dumps(resp.json()['data'], ensure_ascii=False))


class MergedTotalTests(TestCase):
    """修复 7：列表与总数合并为一个请求"""

    def test_total_returned_when_requested(self):
        with mock.patch.object(publicview.iaq, 'query_message1', return_value=[]), \
             mock.patch.object(publicview.iaq, 'query_message_total',
                               return_value={'c': 77}) as mt:
            resp = login_client().post('/pv/other', **_post({**BASE, 'needTotal': True}))
        self.assertEqual(resp.json()['data']['total'], 77)
        mt.assert_called_once()

    def test_count_skipped_when_paging(self):
        """翻页不重新 COUNT：带模糊条件时 COUNT 是扫表，翻页没必要重复付这个代价"""
        with mock.patch.object(publicview.iaq, 'query_message1', return_value=[]), \
             mock.patch.object(publicview.iaq, 'query_message_total',
                               return_value={'c': 77}) as mt:
            resp = login_client().post('/pv/other', **_post({**BASE, 'page': 2}))
        self.assertNotIn('total', resp.json()['data'])
        mt.assert_not_called()


class OperatorListTests(TestCase):
    """修复 8：操作人列表排除已删除记录 + 结果缓存"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # mysqlite 的 migrations 是空包，Django 视其为「已迁移应用」且模型 managed=False，
        # 测试库不会自动建 q_getmessage 表，这里按生产库结构手工建一张
        with connection.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS q_getmessage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uid INTEGER NULL,
                    uname TEXT NULL,
                    q_env TEXT NULL,
                    company_id TEXT NULL,
                    company_name TEXT NULL,
                    message TEXT NULL,
                    status INTEGER NOT NULL DEFAULT 0,
                    data_source INTEGER NULL,
                    server_side INTEGER NULL,
                    version INTEGER NULL,
                    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    update_time TIMESTAMP NULL
                )
            """)

    def setUp(self):
        cache.delete('other:operators')
        self.iaq = InputAndQuery()

    def tearDown(self):
        cache.delete('other:operators')

    def test_excludes_soft_deleted(self):
        QGetMessage.objects.create(uname='alice', status=0, message='x')
        QGetMessage.objects.create(uname='ghost', status=1, message='x')
        names = [r['uname'] for r in self.iaq.query_opraterName()]
        self.assertIn('alice', names)
        self.assertNotIn('ghost', names)

    def test_result_is_cached(self):
        QGetMessage.objects.create(uname='bob', status=0, message='x')
        first = self.iaq.query_opraterName()
        QGetMessage.objects.create(uname='carol', status=0, message='x')
        self.assertEqual(first, self.iaq.query_opraterName())


class TimeRangeTests(TestCase):
    """修复 9：操作时间范围筛选 + 深分页保护"""

    def _call_args(self, **extra):
        with mock.patch.object(publicview.iaq, 'query_message1', return_value=[]) as m:
            login_client().post('/pv/other', **_post({**BASE, **extra}))
        return m.call_args[0]

    def test_range_parsed_and_passed(self):
        """query_message1(num, p, kw, start, end)"""
        args = self._call_args(start='2026-01-01', end='2026-01-31')
        self.assertEqual(args[3], datetime(2026, 1, 1, 0, 0, 0))
        self.assertEqual(args[4], datetime(2026, 1, 31, 23, 59, 59))

    def test_end_date_covers_whole_day(self):
        """截止日必须补到 23:59:59，否则当天记录会被漏掉"""
        args = self._call_args(start='2026-01-01', end='2026-01-01')
        self.assertEqual(args[4], datetime(2026, 1, 1, 23, 59, 59))

    def test_invalid_date_ignored(self):
        args = self._call_args(start='不是日期', end='2026-13-45')
        self.assertIsNone(args[3])
        self.assertIsNone(args[4])

    def test_deep_offset_rejected(self):
        resp = login_client().post('/pv/other', **_post({**BASE, 'num': 10, 'page': 2000}))
        d = resp.json()['data']
        self.assertFalse(d['ok'])
        self.assertIn('筛选', d['errmsg'])
