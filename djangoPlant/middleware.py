# middleware.py
from django.conf import settings

class NoGzipForSSEMiddleware:
    """SSE 流式响应强制不走 GZip 压缩 — 排在第一位确保响应阶段最后执行，覆盖 GZip"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        ct = response.get('Content-Type', '')
        if not (getattr(response, 'streaming', False) and 'text/event-stream' in ct):
            return response
        # 移除 Content-Encoding，浏览器拿裸文本流，逐 token 即时可见
        if response.has_header('Content-Encoding'):
            del response['Content-Encoding']
        response['X-Accel-Buffering'] = 'no'
        return response

class StaticCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/static/'):
            response['Cache-Control'] = 'public, max-age=86400'
        return response

class SessionDataMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 从session中获取需要的数据
        request.rn = request.session.get("rn")
        request.uid = request.session.get('uid')
        request.mr = request.session.get('mr')
        request.islogin = request.session.get("isLoggedIn")
        response = self.get_response(request)
        return response

from django.contrib.auth import logout # type: ignore
from django.http import HttpResponseRedirect # type: ignore
from django.urls import reverse,resolve # type: ignore
from django.core.cache import cache # type: ignore

class SessionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 仅对已登录用户检查session有效性
        if request.user.is_authenticated:
            # 检查关键session变量是否存在
            if not request.session.get('isLoggedIn'):
                # session已失效，强制退出登录
                logout(request)
                if request.method == 'GET':
                    request.session['login_redirect'] = request.get_full_path()
                return HttpResponseRedirect(reverse('login'))
                
        response = self.get_response(request)
        return response

from djangoPlant.menu_registry import match_menu_key

class MenuPermissionMiddleware:
    """菜单权限拦截：已登录用户访问无权限菜单 URL 时，统一跳转无权限页"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            menu_key, matched = match_menu_key(request.path)
            if matched and menu_key not in request.session.get('menus', []):
                return HttpResponseRedirect('/denied')
        return self.get_response(request)

import json
import logging

logger = logging.getLogger('api')


class SuppressNoiseFilter(logging.Filter):
    """屏蔽日志噪音：浏览器 devtools 请求 sourcemap、favicon 等产生的 404"""
    NOISE = ('.map', '/.well-known/', 'favicon.ico')

    def filter(self, record):
        msg = record.getMessage()
        return not any(n in msg for n in self.NOISE)


class ResponseLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # 只记录业务接口，静态资源/后台不记录
        path = request.path
        if path.startswith('/static/') or path.startswith('/admin'):
            return response

        ct = response.get('Content-Type', '')
        is_api = ct.startswith('application/json') or ct.startswith('text/event-stream')
        if not is_api:
            return response

        # 流式响应（SSE 等）：不读 content（会触发缓冲），只记元信息
        if getattr(response, 'streaming', False):
            logger.info(f"API: {request.method} {path} → {response.status_code} (streaming)")
            return response

        try:
            body = response.content.decode('utf-8')
            logger.info(f"API: {request.method} {path} → {response.status_code} ({len(body)} bytes)")
        except UnicodeDecodeError:
            logger.info(f"API: {request.method} {path} → {response.status_code} ({len(response.content)} bytes)")

        return response

