from django.test import TestCase, Client
from django.contrib.auth.models import User
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DIST_INDEX = BASE_DIR / 'static' / 'vue' / 'index.html'


class SpaFallbackTests(TestCase):
    def test_spa_index_returns_html_when_dist_exists(self):
        # 造一个临时 static/vue/index.html
        DIST_INDEX.parent.mkdir(parents=True, exist_ok=True)
        DIST_INDEX.write_text('<!DOCTYPE html><div id="app"></div>', encoding='utf-8')
        try:
            resp = Client().get('/some-vue-route')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp['Content-Type'], 'text/html')
            self.assertIn(b'<div id="app">', resp.content)
        finally:
            DIST_INDEX.unlink(missing_ok=True)

    def test_spa_index_404_when_dist_missing(self):
        if DIST_INDEX.exists():
            DIST_INDEX.unlink()
        resp = Client().get('/some-vue-route')
        self.assertEqual(resp.status_code, 404)

    def test_root_returns_spa(self):
        # 根路径 / 应返回 Vue index.html（登录后进入 Vue 壳）
        DIST_INDEX.parent.mkdir(parents=True, exist_ok=True)
        DIST_INDEX.write_text('<!DOCTYPE html><div id="app"></div>', encoding='utf-8')
        try:
            resp = Client().get('/')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'<div id="app">', resp.content)
        finally:
            DIST_INDEX.unlink(missing_ok=True)


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
