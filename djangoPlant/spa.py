"""SPA 兜底视图：生产环境下把非 API 路径交给 Vue 的 index.html。"""
from pathlib import Path
from django.http import HttpResponse, Http404
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie

BASE_DIR = Path(__file__).resolve().parent.parent
DIST_INDEX = BASE_DIR / 'static' / 'vue' / 'index.html'


@never_cache
@ensure_csrf_cookie
def spa_index(request):
    """返回 Vue 构建产物 index.html，让 vue-router 接管前端路由。
    @ensure_csrf_cookie 确保首次加载时设置 CSRF cookie，供后续 POST 请求使用。"""
    if not DIST_INDEX.exists():
        raise Http404("前端尚未构建，请先运行 frontend 的 npm run build")
    with open(DIST_INDEX, 'rb') as f:
        return HttpResponse(f.read(), content_type='text/html')
