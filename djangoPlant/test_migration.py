from django.test import TestCase, Client
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
