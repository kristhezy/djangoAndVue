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
