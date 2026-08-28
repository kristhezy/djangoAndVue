import logging,re,requests,datetime,random,json,hashlib,html,io,os,time,ast # type: ignore
from pathlib import Path
from collections import Counter

# pymysql NULL 常量（本来是 from pymysql import NULL，改为直接定义避免加载 pymysql）
NULL = "NULL"
from time import strftime,localtime
from urllib.parse import urlencode
from django.shortcuts import render,redirect # type: ignore
from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse # type: ignore
from django.http import JsonResponse as _JsonResponse  # type: ignore

# 包装 JsonResponse，默认 ensure_ascii=False，让中文在抓包工具中正常显示
def JsonResponse(data, **kwargs):
    kwargs.setdefault('json_dumps_params', {'ensure_ascii': False})
    return _JsonResponse(data, **kwargs)
from django.conf import settings # type: ignore
from django.contrib.auth import authenticate, login, logout # type: ignore
from django.contrib.auth.hashers import make_password # type: ignore
from django.contrib.auth.decorators import login_required # type: ignore
from django.views.decorators.cache import never_cache,cache_page # type: ignore
from django.core.cache import cache  # type: ignore
from django.views.decorators.csrf import csrf_exempt # type: ignore
from.functionTools import handle_request_errors

# 获取日志记录器
logger = logging.getLogger(__name__)
# 获取当前脚本所在目录
current_dir = Path(__file__).parent.parent


# 定义颜色常量
class Colors:
    RESET = '\033[0m'     # 重置所有格式
    RED = '\033[31m'      # 红色
    GREEN = '\033[32m'    # 绿色
    YELLOW = '\033[33m'   # 黄色
    BLUE = '\033[34m'     # 蓝色
    MAGENTA = '\033[35m'  # 品红色
    CYAN = '\033[36m'     # 青色
    BOLD = '\033[1m'       # 加粗
    UNDERLINE = '\033[4m'  # 下划线


