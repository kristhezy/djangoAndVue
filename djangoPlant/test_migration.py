from django.test import TestCase, Client
from django.contrib.auth.models import User
from pathlib import Path
from unittest import mock
import tempfile

from djangoPlant import spa


class SpaFallbackTests(TestCase):
    """SPA 兜底视图测试：用 mock 把 spa.DIST_INDEX 指向临时文件，绝不触碰真实
    static/vue/ 构建产物（否则跑测试会删掉生产构建的 index.html，导致 / 404）。"""

    def test_spa_index_returns_html_when_dist_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            idx = Path(tmp) / 'index.html'
            idx.write_text('<!DOCTYPE html><div id="app"></div>', encoding='utf-8')
            with mock.patch.object(spa, 'DIST_INDEX', idx):
                resp = Client().get('/some-vue-route')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/html')
        self.assertIn(b'<div id="app">', resp.content)

    def test_spa_index_404_when_dist_missing(self):
        missing = Path(tempfile.gettempdir()) / 'definitely-not-exists' / 'index.html'
        with mock.patch.object(spa, 'DIST_INDEX', missing):
            resp = Client().get('/some-vue-route')
        self.assertEqual(resp.status_code, 404)

    def test_root_returns_spa(self):
        # 根路径 / 应返回 Vue index.html（登录后进入 Vue 壳）
        with tempfile.TemporaryDirectory() as tmp:
            idx = Path(tmp) / 'index.html'
            idx.write_text('<!DOCTYPE html><div id="app"></div>', encoding='utf-8')
            with mock.patch.object(spa, 'DIST_INDEX', idx):
                resp = Client().get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'<div id="app">', resp.content)


class MenuApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('menutest', password='x')
        self.c = Client()
        self.c.force_login(self.user)
        # SessionExpiryMiddleware 要求已登录用户 session 里有 isLoggedIn，
        # 否则会 logout 并 302 到 /login（与真实 user_login 流程一致）。
        s = self.c.session
        s['isLoggedIn'] = True
        s.save()

    def test_requires_login(self):
        resp = Client().get('/api/menu')
        self.assertIn(resp.status_code, (302, 403))

    def test_empty_menus_returns_empty(self):
        resp = self.c.get('/api/menu')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()['data']
        self.assertEqual(data['standalone'], [])
        self.assertEqual(data['groups'], [])

    def test_mergeuser_menu_is_inside_tools_group(self):
        # 只给 mergeUser 权限
        s = self.c.session
        s['menus'] = ['mergeUser']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        self.assertEqual(data['standalone'], [])
        self.assertEqual(len(data['groups']), 1)
        self.assertEqual(data['groups'][0]['key'], 'tools')
        self.assertEqual(data['groups'][0]['items'][0]['key'], 'mergeUser')

    def test_migrated_menu_url_rewritten_to_frontend_path(self):
        # 已迁移页的菜单 url 改写为独立前端路径，避免与真实旧路由冲突（刷新仍走 Vue 版）
        s = self.c.session
        s['menus'] = ['mergeUser']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        item = data['groups'][0]['items'][0]
        self.assertEqual(item['url'], '/mergeUser')

    def test_other_menu_url_rewritten_to_frontend_path(self):
        s = self.c.session
        s['menus'] = ['other']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        # other 是 standalone 菜单
        item = next(x for x in data['standalone'] if x['key'] == 'other')
        self.assertEqual(item['url'], '/other')

    def test_mynote_menu_url_rewritten_to_frontend_path(self):
        s = self.c.session
        s['menus'] = ['mynote']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        # mynote 是 standalone 菜单
        item = next(x for x in data['standalone'] if x['key'] == 'mynote')
        self.assertEqual(item['url'], '/mynote')

    def test_delcp_menu_url_rewritten_to_frontend_path(self):
        s = self.c.session
        s['menus'] = ['delCP']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        # delCP 在 tools 分组里
        item = next(x for x in data['groups'][0]['items'] if x['key'] == 'delCP')
        self.assertEqual(item['url'], '/delCP')

    def test_batchdeleteclue_menu_url_rewritten_to_frontend_path(self):
        s = self.c.session
        s['menus'] = ['batchDeleteClue']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        # batchDeleteClue 在 tools 分组里
        item = next(x for x in data['groups'][0]['items'] if x['key'] == 'batchDeleteClue')
        self.assertEqual(item['url'], '/batchDeleteClue')

    def test_forwecom_menu_url_rewritten_to_frontend_path(self):
        s = self.c.session
        s['menus'] = ['forWeCom']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        # forWeCom 在 tools 分组里
        item = next(x for x in data['groups'][0]['items'] if x['key'] == 'forWeCom')
        self.assertEqual(item['url'], '/forWeCom')

    def test_delbindrelation_menu_url_rewritten_to_frontend_path(self):
        s = self.c.session
        s['menus'] = ['delBindRelation']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        # delBindRelation 在 tools 分组里
        item = next(x for x in data['groups'][0]['items'] if x['key'] == 'delBindRelation')
        self.assertEqual(item['url'], '/delBindRelation')

    def test_aboutlogin_menu_url_rewritten_to_frontend_path(self):
        s = self.c.session
        s['menus'] = ['aboutLogin']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        # aboutLogin 在 tools 分组里
        item = next(x for x in data['groups'][0]['items'] if x['key'] == 'aboutLogin')
        self.assertEqual(item['url'], '/aboutLogin')

    def test_dzfunction_menu_url_rewritten_to_frontend_path(self):
        s = self.c.session
        s['menus'] = ['dzFunction']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        # dzFunction 在 tools 分组里
        item = next(x for x in data['groups'][0]['items'] if x['key'] == 'dzFunction')
        self.assertEqual(item['url'], '/dzFunction')

    def test_jtsaleskits_menu_url_rewritten_to_frontend_path(self):
        s = self.c.session
        s['menus'] = ['jtSaleskits']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        # jtSaleskits 在 compconfig 分组里
        item = next(x for x in data['groups'][0]['items'] if x['key'] == 'jtSaleskits')
        self.assertEqual(item['url'], '/jtSaleskits')

    def test_hwskset_menu_url_rewritten_to_frontend_path(self):
        s = self.c.session
        s['menus'] = ['hwskset']
        s.save()
        resp = self.c.get('/api/menu')
        data = resp.json()['data']
        # hwskset 在 compconfig 分组里
        item = next(x for x in data['groups'][0]['items'] if x['key'] == 'hwskset')
        self.assertEqual(item['url'], '/hwskset')
