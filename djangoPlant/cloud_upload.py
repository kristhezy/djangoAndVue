"""
云图片上传 — 登录 → 上传 → 返回图片链接。失败时回退本地 base64。
"""
import time, logging
import requests
from django.core.cache import cache  # type: ignore

logger = logging.getLogger(__name__)

_CLOUD_BASE = "https://borigin-test.aijiatui.com"
_LOGIN_URL = f"{_CLOUD_BASE}/admin/login/account"
_UPLOAD_URL = f"{_CLOUD_BASE}/admin/uploadFile"
_LOGIN_PHONE = "17600000015"
_LOGIN_PASSWORD = "ce00580d6b3d1e0d7b7b8ec5eab0bc89"

_TOKEN_CACHE_KEY = "cloud_upload:token"
_TOKEN_CACHE_TTL = 36000  # token 缓存 10 小时


def _get_token() -> str:
    """获取上传 token，缓存 10 小时"""
    token = cache.get(_TOKEN_CACHE_KEY)
    if token:
        return token

    try:
        resp = requests.post(
            _LOGIN_URL,
            json={"phone": _LOGIN_PHONE, "password": _LOGIN_PASSWORD},
            timeout=5,
        )
        data = resp.json()
        if data.get("code") == 0 and data.get("data"):
            token = data["data"][0]["token"]
            cache.set(_TOKEN_CACHE_KEY, token, _TOKEN_CACHE_TTL)
            logger.info(f"[云上传] 登录成功 token={token[:8]}…")
            return token
        else:
            logger.error(f"[云上传] 登录失败: {data.get('msg','')}")
            return ""
    except Exception as e:
        logger.error(f"[云上传] 登录异常: {e}")
        return ""


def upload_image(file_bytes: bytes, filename: str = "image.png") -> str:
    """
    上传图片到云端，返回图片 URL。
    失败时返回空字符串，调用方应回退到 base64 本地存储。
    """
    token = _get_token()
    if not token:
        return ""

    try:
        resp = requests.post(
            _UPLOAD_URL,
            headers={"i-token": token},
            files={"image": (filename, file_bytes, "image/png")},
            timeout=10,
        )
        data = resp.json()
        if data.get("code") == 0:
            url = data.get("data", "")
            if url:
                logger.info(f"[云上传] 成功 {url[:60]}")
                return url
            else:
                logger.error(f"[云上传] 返回无 data 字段: {data}")
                return ""
        elif data.get("code") == 43265:
            # token 过期，清缓存下次重登
            logger.warning("[云上传] token 过期，清除缓存")
            cache.delete(_TOKEN_CACHE_KEY)
            return ""
        else:
            logger.error(f"[云上传] 失败 code={data.get('code')} msg={data.get('msg','')}")
            return ""
    except Exception as e:
        logger.error(f"[云上传] 异常: {e}")
        return ""
