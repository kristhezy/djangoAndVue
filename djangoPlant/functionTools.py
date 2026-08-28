import requests, datetime, traceback
import functools

# 定义颜色常量
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

STATUS_MAP = {
    200: None,
    400: "❌ 400,请求格式不正确",
    401: "❌ 401,未授权",
    403: "❌ 403,禁止访问",
    413: "❌ 413,文件过大",
    404: "❌ 404,接口未找到",
    500: "💥 500,服务器内部错误",
    502: "⚠️ 502,服务暂时不可用",
    503: "⚠️ 503,服务暂时不可用",
}

def gctime():
    c_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return c_time


def _format_args(args, kwargs):
    """格式化函数调用参数，便于日志输出"""
    # 跳过第一个参数 self/cls
    parts = []
    for a in args[1:]:
        parts.append(repr(a))
    for k, v in kwargs.items():
        parts.append(f"{k}={repr(v)}")
    return ', '.join(parts) if parts else '(无参数)'


def _safe_truncate(obj, max_len=500):
    """安全截断字符串，避免响应体过长刷屏"""
    s = str(obj)
    if len(s) > max_len:
        return s[:max_len] + f"... [截断，总长度={len(s)}]"
    return s


def handle_request_errors(status_map=None):
    """
    统一装饰器，支持调用模式：
    模式1 — 函数自行执行HTTP请求（返回 requests.Response 或 dict）：
        @handle_request_errors()
        def foo(self, ...):
            res = session.post(url, json=data)
            return res   # Response 对象 → 装饰器校验状态码、返回 .json()
                          # dict          → 直接透传
    """
    if status_map is None:
        status_map = STATUS_MAP

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            call_args = _format_args(args, kwargs)
            try:
                result = func(*args, **kwargs)

                # ---- 模式2：函数返回 (remark, url, header, payload) 元组 ----
                if isinstance(result, tuple) and len(result) == 4:
                    remark, url, header, payload = result
                    res = requests.post(url, headers=header, json=payload)
                    status_code = res.status_code
                    msg = status_map.get(status_code)
                    if msg:
                        resp_body = _safe_truncate(res.text)
                        print(f"❌ {func.__name__} -> {msg}")
                        print(f"   请求URL: {url}")
                        print(f"   请求参数: {_safe_truncate(payload)}")
                        print(f"   响应体:   {resp_body}")
                        return None
                    rlt = res.json()
                    print(f"{BOLD}{gctime()} {BLUE}{remark}{RESET}{rlt}")
                    return rlt

                # ---- 模式1：函数自行执行请求 ----
                if not hasattr(result, 'status_code'):
                    # 已经是 dict（可能已被 .json() 处理），直接透传
                    return result
                status_code = result.status_code
                msg = status_map.get(status_code)
                if msg:
                    resp_body = _safe_truncate(result.text)
                    print(f"❌ {func.__name__} -> {msg}")
                    print(f"   请求URL:  {result.request.url if result.request else '未知'}")
                    print(f"   请求方法: {result.request.method if result.request else '未知'}")
                    print(f"   请求体:   {_safe_truncate(result.request.body) if result.request else '未知'}")
                    print(f"   响应体:   {resp_body}")
                    return {"code": status_code, "msg": msg, "data": ""}
                return result.json()

            except requests.exceptions.Timeout as e:
                print(f"⏰ [{gctime()}] {func.__name__} -> 请求超时")
                print(f"   调用参数: {call_args}")
                print(f"   详细信息: {e}")
            except requests.exceptions.ConnectionError as e:
                print(f"🔌 [{gctime()}] {func.__name__} -> 网络连接错误")
                print(f"   调用参数: {call_args}")
                print(f"   详细信息: {e}")
            except Exception as e:
                tb_lines = traceback.format_exc()
                print(f"💥 [{gctime()}] {func.__name__} -> 未预期错误")
                print(f"   调用参数: {call_args}")
                print(f"   异常类型: {type(e).__name__}")
                print(f"   异常信息: {e}")
                # 只打印最后 8 行 traceback，避免刷屏
                short_tb = '\n'.join(tb_lines.split('\n')[-10:]) if len(tb_lines.split('\n')) > 10 else tb_lines
                print(f"   堆栈追踪:\n{short_tb}")
        return wrapper
    return decorator
