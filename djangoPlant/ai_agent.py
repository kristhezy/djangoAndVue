# -*- coding: utf-8 -*-
"""
LangGraph ReAct Agent —— 项目专属 AI 助手（原生融入 Django）

由 myAgent 移植而来，改造点：
  1. 懒加载 langgraph / langchain（首次调用才 import，避免拖慢 Django 启动）
  2. 搜索工具复用项目已有的 Serper（ai_xfxh.search_web，带 Redis 缓存）
  3. 新增企业信息 / 用户信息查询工具（包装 QueryInterface）
  4. 日志分析能力通过 system prompt 强化（无需外部接口）
  5. 复用 ai_xfxh 的 DeepSeek 配置（同一 key / 同一模型）
"""
import json
import logging
import queue as _queue
import threading as _threading
import time as _time
import uuid as _uuid

# 轻量级顶层 import（ai_xfxh 已被 publicview 加载，常量零成本）
from .ai_xfxh import DS_API_KEY, DS_BASE_URL, DS_MODEL, DS_THINKING_OFF, search_web, _translate_error

logger = logging.getLogger(__name__)

# ── 执行上限（成本/失控兜底）──
MAX_STEPS = 15          # ReAct 最大步数（LangGraph recursion_limit，默认 25）
AGENT_TIMEOUT = 60      # 单次请求整体墙钟超时（秒）
LLM_TIMEOUT = 60        # 单次 LLM 调用超时（秒）
LLM_MAX_RETRIES = 1     # LLM 调用重试次数
TOOL_TIMEOUT = 15       # 单个工具（尤其外部 HTTP）超时（秒），避免拖到全局 60s
MAX_TOKENS = 2048       # 单次 LLM 输出上限（DeepSeek 默认 4096，这里收紧）
TOOL_RESULT_MAX_CHARS = 4000  # 单个工具返回内容上限（字符），超出截断，避免回喂 LLM 撑爆上下文

_WEEKDAYS = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")


def _ok(data, limit=TOOL_RESULT_MAX_CHARS):
    """工具成功返回：{"ok": true, "data": ...}；data 过长时截断，避免回喂 LLM 撑爆上下文。"""
    if isinstance(data, str):
        orig = len(data)
        if orig > limit:
            data = data[:limit] + f"\n…（结果过长已截断，原 {orig} 字符）"
    return json.dumps({"ok": True, "data": data}, ensure_ascii=False)


def _fail(code, error):
    """工具失败返回：{"ok": false, "code": ..., "error": ...}"""
    return json.dumps({"ok": False, "code": code, "error": error}, ensure_ascii=False)


def _now_context() -> str:
    """返回当前日期时间（中文，精确到分钟），注入给 LLM，避免其凭训练数据猜日期。

    精确到分钟而非秒：DeepSeek 的前缀缓存要求 system 消息前缀逐字节一致，
    精确到秒会让每次请求的前缀都不同、缓存永远 miss；降为分钟可在同一分钟内命中缓存。
    """
    from datetime import datetime
    now = datetime.now()
    return f"现在是 {now.strftime('%Y年%m月%d日')} {_WEEKDAYS[now.weekday()]} {now.strftime('%H:%M')}。"


SYSTEM_PROMPT = """你是「django项目」的专属运维助手--小木，服务于公司内部技术平台后台。

你的能力：
1. 企业信息查询 —— 用 query_company_info / query_company_module / query_company_payment 工具查企业的基本信息、开通的功能模块、打款方式。当用户只提供登录账号时，用 query_company_info_by_loginName 查其所属企业。用 query_company_op_log 查企业/操作人的操作流水（全项目）。
2. 用户信息查询 —— 用 query_user_info / query_user_by_company_phone 工具按 userId 或「企业ID+手机号」查平台用户；用 query_mmeett_user 查 mmeett 用户详情（用户ID/推荐码/会员等级/昵称/邮箱/国家码）。
3. 联网搜索 —— 用 web_search 工具查天气、新闻、股价、汇率、最新资讯、文档、报错解决方案等实时信息。凡是你不知道的实时/时效性内容（天气、今天发生的事、最新价格等），都必须先调用 web_search，不得凭猜测回答或声称"没有查询能力"。
4. 日志排查 —— 用 read_logs 工具读取项目日志（logs/ 目录）定位最近的问题；用户直接粘贴报错日志/异常堆栈时，也按以下结构分析：
   【错误类型】一句话概括
   【根因分析】定位最可能的根本原因
   【修复建议】给出具体可执行的修复步骤（含代码示例时用 Markdown 代码块）
5. mmeett 操作汇总 —— 用 query_mmeett_ops 工具查询 mmeettOpen 页面的操作记录，按用户/环境/操作类型/时间汇总用户做过的操作（如注册、购买会员、发放算力、安置等）及结果。
6. 小程序记录 —— 用 query_miniprogram_record 工具按手机号/企业ID/企业名/app_id 查小程序记录。

规则：
- 环境参数 env 由你根据用户提问判断：提到"生产/正式/线上"用 prod，提到"测试"用 test；未明确时默认 prod。
- 涉及技术问题时提供代码示例和分步说明；分析问题时提供多角度观点。
- 用中文回答，Markdown 格式组织内容。
- 查询无结果时如实告知，不要编造数据。
- 你拥有 web_search 联网搜索工具。遇到任何实时/时效性问题（如天气、新闻、价格、汇率、今天发生的事），必须调用 web_search 获取结果后再回答；严禁在未调用工具的情况下回复"无法查询""没有实时能力"之类的说法。

工具返回格式：每个工具都返回 JSON 字符串——成功为 {"ok": true, "data": "..."}（data 可能是普通文本，也可能是另一层 JSON 字符串），失败为 {"ok": false, "code": "...", "error": "..."}。请依据 ok 字段判断结果：ok=false 时向用户如实说明 error 中的原因，不要编造数据。"""


_agent = None


def _build_llm(temperature=0.7, max_tokens=MAX_TOKENS):
    """构建一个轻量 ChatOpenAI 客户端（不进 ReAct，供直通回答 / 分类器复用）。

    max_tokens 经 extra_body 透传：DeepSeek 只认 max_tokens（忽略 max_completion_tokens），
    而 langchain_openai 会把顶层的 max_tokens 字段自动改名成 max_completion_tokens，导致设了无效。
    stream_usage=True 让流式最后一个 chunk 携带 usage_metadata（token 用量），供成本统计。
    """
    from langchain_openai import ChatOpenAI  # type: ignore
    return ChatOpenAI(
        model=DS_MODEL,
        api_key=DS_API_KEY,
        base_url=DS_BASE_URL,
        temperature=temperature,
        streaming=True,
        request_timeout=LLM_TIMEOUT,
        max_retries=LLM_MAX_RETRIES,
        stream_usage=True,
        extra_body={"max_tokens": max_tokens, **DS_THINKING_OFF},
    )


def _with_timeout(func, timeout=TOOL_TIMEOUT):
    """给工具函数加墙钟超时（重点保护外部 HTTP，避免单个工具卡住拖到全局 60s）。

    用一个 daemon 线程执行 func，主线程带超时 join；超时返回 _fail("TOOL_TIMEOUT", ...)。
    """
    result = {}
    done = False

    def _runner():
        nonlocal result, done
        try:
            result = func()
        except Exception as e:
            result = _fail("TOOL_ERROR", str(e)[:200])
        finally:
            done = True

    t = _threading.Thread(target=_runner, daemon=True)
    t.start()
    t.join(timeout)
    if not done:
        return _fail("TOOL_TIMEOUT", f"工具执行超过 {timeout} 秒")
    return result


def _log_usage(rid, usage):
    """记录一次 LLM 调用的 token 用量（stream_usage 在最后一个 chunk 带上 usage_metadata）。

    cache_read 即 DeepSeek 前缀缓存命中 token 数（DeepSeek 填 OpenAI 官方 cached_tokens，
    langchain 映射到 usage_metadata.input_token_details.cache_read）。注意：缓存最小单元
    为 64 token，短 prompt（<64 token）不会命中；长前缀（SYSTEM_PROMPT + 工具 schema）收益最大。
    """
    if not usage:
        logger.info("[Agent][req=%s] token 用量未获取", rid)
        return
    try:
        i = getattr(usage, "input_tokens", None) or usage.get("input_tokens")
        o = getattr(usage, "output_tokens", None) or usage.get("output_tokens")
        t = getattr(usage, "total_tokens", None) or usage.get("total_tokens")
        details = usage.get("input_token_details") if isinstance(usage, dict) else getattr(usage, "input_token_details", None)
        cr = (details or {}).get("cache_read") if isinstance(details, dict) else None
        logger.info(
            "[Agent][req=%s] token 用量 input=%s output=%s total=%s cache_read=%s",
            rid, i, o, t, cr,
        )
    except Exception:
        logger.info("[Agent][req=%s] token 用量 %s", rid, usage)


def _get_agent():
    """懒加载单例：首次调用才 import langgraph + 构建 agent。"""
    global _agent
    if _agent is None:
        from langchain_core.tools import tool  # type: ignore
        from langgraph.prebuilt import create_react_agent  # type: ignore
        from .QueryInterface import QueryInterface as _QI
        from .query_everything import queryEverything as _QE
        from .pub_InputAndQuery import InputAndQuery as _IAQ
        from .mmeett import mmeettIF as _MM

        qi = _QI()
        qe = _QE()
        iaq = _IAQ()
        mm = _MM()

        # ── 工具：联网搜索（复用项目 Serper）──
        @tool
        def web_search(query: str) -> str:
            """联网搜索获取实时信息。当用户询问天气、新闻、股价、汇率、最新资讯、技术文档、报错解决方案，或任何你不知道的实时/时效性内容时，务必调用本工具。"""
            try:
                r = search_web(query)
                if isinstance(r, str) and r.startswith("【Serper 搜索】"):
                    return _fail("WEB_SEARCH_ERROR", r)
                return _ok(r)
            except Exception as e:
                return _fail("WEB_SEARCH_ERROR", str(e)[:200])

        # ── 工具：读取日志（定位问题）──
        @tool
        def read_logs(keyword: str = "", lines: int = 100) -> str:
            """读取项目日志（logs/ 目录）以定位最近的问题。
            keyword 可选，用于过滤日志行（如错误信息、接口路径、异常类型）；lines 为每个文件最多返回的行数（默认 100）。
            当需要排查报错、查看接口调用记录、定位异常时使用。"""
            try:
                from pathlib import Path
                from django.conf import settings
                log_dir = Path(settings.LOG_DIR)
                if not log_dir.exists():
                    return _ok("logs/ 目录不存在")
                files = sorted(log_dir.glob('*.log'), key=lambda p: p.stat().st_mtime, reverse=True)
                if not files:
                    return _ok("logs/ 目录下暂无日志文件")
                out = []
                for f in files[:3]:
                    try:
                        raw = f.read_text(encoding='utf-8', errors='ignore').splitlines()
                    except Exception:
                        continue
                    if keyword:
                        raw = [l for l in raw if keyword in l]
                    if raw:
                        out.append(f"===== {f.name} =====")
                        out.extend(raw[-lines:])
                if not out:
                    return _ok(f"未找到匹配「{keyword}」的日志" if keyword else "日志为空")
                return _ok("\n".join(out[-lines * 2:]))
            except Exception as e:
                return _fail("READ_LOGS_ERROR", str(e)[:200])

        # ── 工具：企业信息 ──
        @tool
        def query_company_info(company_id: str, env: str = "prod") -> str:
            """查询企业基本信息。company_id 为企业ID；env 环境：test(测试)/prod(生产)，默认 prod。"""
            try:
                r = qi.query_companyInfo(company_id, env)
                return _ok(json.dumps(r, ensure_ascii=False)) if r else _ok("未查询到该企业信息")
            except Exception as e:
                return _fail("QUERY_COMPANY_INFO_ERROR", str(e)[:200])

        @tool
        def query_company_module(company_id: str, env: str = "prod") -> str:
            """查询企业已开通的功能模块列表。company_id 为企业ID；env 环境：test/prod，默认 prod。"""
            try:
                r = qi.query_companyModule(company_id, env)
                return _ok(json.dumps(r, ensure_ascii=False)) if r else _ok("未查询到该企业模块信息")
            except Exception as e:
                return _fail("QUERY_COMPANY_MODULE_ERROR", str(e)[:200])

        @tool
        def query_company_payment(company_id: str, env: str = "prod") -> str:
            """查询企业的打款方式。company_id 为企业ID；env 环境：test/prod，默认 prod。"""
            try:
                r = qi.query_companyPayment(company_id, env)
                return _ok(json.dumps(r, ensure_ascii=False)) if r else _ok("未查询到该企业打款信息")
            except Exception as e:
                return _fail("QUERY_COMPANY_PAYMENT_ERROR", str(e)[:200])

        # ── 工具：用户信息 ──
        @tool
        def query_user_info(user_id: str, env: str = "prod") -> str:
            """根据 userId 查询用户信息。user_id 为用户ID；env 环境：test/prod，默认 prod。"""
            try:
                r = qi.query_userInfo(user_id, env)
                return _ok(json.dumps(r, ensure_ascii=False)) if r else _ok("未查询到该用户信息")
            except Exception as e:
                return _fail("QUERY_USER_INFO_ERROR", str(e)[:200])

        @tool
        def query_user_by_company_phone(company_id: str, phone: str, env: str = "prod") -> str:
            """根据「企业ID + 手机号」查询用户信息。company_id 为企业ID；phone 为手机号；env 环境：test/prod，默认 prod。"""
            try:
                r = qi.query_uidbyCP(company_id, phone, env)
                return _ok(json.dumps(r, ensure_ascii=False)) if r else _ok("未查询到该用户信息")
            except Exception as e:
                return _fail("QUERY_USER_BY_PHONE_ERROR", str(e)[:200])

        @tool
        def query_company_info_by_loginName(loginName: str, env: str = "prod") -> str:
            """根据登录账号/手机号(loginName)查询其所属企业信息。loginName 为登录账号/手机号；env 环境：test(测试)/prod(生产)，默认 prod。"""
            try:
                r = qe.query_companyId(loginName, env)
                return _ok(json.dumps(r, ensure_ascii=False)) if r else _ok("未查询到该登录账号对应的企业信息")
            except Exception as e:
                return _fail("QUERY_COMPANY_BY_LOGINNAME_ERROR", str(e)[:200])

        # ── 工具：mmeett 操作汇总 ──
        @tool
        def query_mmeett_ops(env: str = "", action: str = "", user_id: str = "", days: int = 0, limit: int = 200) -> str:
            """查询并汇总 mmeettOpen 页面的操作日志。env 环境筛选(test/prod，空=全部)；action 操作类型筛选(如 mmeettRegist/buyVip/sendComputing/userSettle，空=全部)；user_id 登录用户ID筛选(空=全部)；days 最近N天(0=不限)；limit 最多返回条数(默认200)。用于汇总用户在 mmeett 页面做过哪些操作、各操作的数量与结果。"""
            try:
                start = ""
                if days and int(days) > 0:
                    from datetime import timedelta
                    from django.utils import timezone as _tz
                    start = (_tz.now() - timedelta(days=int(days))).strftime("%Y-%m-%d %H:%M:%S")
                rows = iaq.query_mmeett_op_log(
                    user_id=user_id, env=env, action=action,
                    start_time=start, limit=limit,
                )
                if not rows:
                    return _ok("暂无 mmeett 操作记录")
                return _ok(json.dumps(rows, ensure_ascii=False))
            except Exception as e:
                return _fail("QUERY_MMEETT_OPS_ERROR", str(e)[:200])

        # ── 工具：企业操作日志（q_getmessage 全项目操作流水）──
        @tool
        def query_company_op_log(keyword: str = "", env: str = "", uname: str = "", limit: int = 50) -> str:
            """查询企业操作日志（q_getmessage 表，全项目操作流水）。keyword 模糊匹配企业名/操作人/操作内容(任一命中)；env 环境筛选(prod/test，空=全部)；uname 操作人精确筛选(空=全部)；limit 最多返回条数(默认50)。用于查某个企业或用户做过哪些操作、操作流水明细。"""
            try:
                rows = iaq.query_message_ops(keyword=keyword, env=env, uname=uname, limit=limit)
                if not rows:
                    return _ok("未查询到操作日志")
                return _ok(json.dumps(rows, ensure_ascii=False))
            except Exception as e:
                return _fail("QUERY_COMPANY_OP_LOG_ERROR", str(e)[:200])

        # ── 工具：mmeett 用户详情 ──
        @tool
        def query_mmeett_user(account: str, env: str = "prod") -> str:
            """查询 mmeett 用户详情。account 为 mmeett 登录用户名(账号/邮箱)；env 环境 test/prod，默认 prod。返回用户ID(jtUserId/userId)、推荐码、会员等级、昵称、邮箱、国家码等。"""
            def _impl():
                version = "7"
                lr = mm.userlogin(account, env, version)
                if not lr or lr.get("code") != 0:
                    return _fail("MMEETT_LOGIN_ERROR", json.dumps(lr, ensure_ascii=False))
                r = mm.queryUserInfo(account, env, version)
                if not r or r.get("code") != 0:
                    return _fail("MMEETT_QUERY_ERROR", json.dumps(r, ensure_ascii=False))
                return _ok(json.dumps(r.get("data", {}).get("user", r), ensure_ascii=False))
            # mmeett 走外部 HTTP，用 _with_timeout 兜底，避免单个工具卡住
            try:
                return _with_timeout(_impl)
            except Exception as e:
                return _fail("MMEETT_USER_ERROR", str(e)[:200])

        # ── 工具：小程序记录 ──
        @tool
        def query_miniprogram_record(keyword: str = "", limit: int = 50) -> str:
            """查询小程序记录。keyword 模糊匹配手机号/企业ID/企业名/app_id；limit 最多返回条数(默认50)。"""
            try:
                rows = iaq.query_mprecord(limit, 0, keyword)
                if not rows:
                    return _ok("未查询到小程序记录")
                return _ok(json.dumps(rows, ensure_ascii=False))
            except Exception as e:
                return _fail("QUERY_MINIPROGRAM_RECORD_ERROR", str(e)[:200])

        llm = _build_llm(0.7)

        _agent = create_react_agent(
            llm,
            tools=[
                web_search,
                read_logs,
                query_company_info,
                query_company_module,
                query_company_payment,
                query_user_info,
                query_user_by_company_phone,
                query_company_info_by_loginName,
                query_mmeett_ops,
                query_company_op_log,
                query_mmeett_user,
                query_miniprogram_record,
            ],
            prompt=SYSTEM_PROMPT,
        )
    return _agent


_prewarmed = False


def prewarm_agent():
    """启动预热：后台线程提前构建 ReAct agent，消除首次调用的 ~14s 懒加载延迟。"""
    global _prewarmed
    if _prewarmed:
        return
    _prewarmed = True

    import threading
    def _warm():
        logger.info("🔥 Agent 预热开始…")
        import time as _t
        t0 = _t.time()
        _get_agent()
        logger.info("🔥 Agent 预热完成 +%.1fs", _t.time() - t0)
    threading.Thread(target=_warm, daemon=True).start()


def _content_to_str(content) -> str:
    """AIMessage.content 可能是 str 或 list[dict]，统一转成纯文本。"""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, dict):
                parts.append(b.get("text", ""))
            else:
                parts.append(str(b))
        return "".join(parts)
    return str(content)


# ── 简单问题直通：分类器 ──
_TOOL_KEYWORDS = (
    "查询", "查一下", "帮我查", "查查", "汇总", "统计", "日志", "搜索", "企业", "公司",
    "用户", "小程序", "操作", "记录", "算力", "会员", "打款", "模块", "流水",
    "环境", "mmeett", "注册", "安置", "开会员", "开通", "报错", "排查", "定位",
    # 实时/联网类 —— 必须走 web_search 才能拿到准确结果
    "天气", "新闻", "股价", "股票", "汇率", "比分", "热搜", "台风", "地震",
    "最新", "今日", "实时", "刚刚", "上映", "票房",
)
_SIMPLE_GREETINGS = (
    "你好", "您好", "hi", "hello", "在吗", "谢谢", "感谢", "再见", "你是谁",
    "你能做什么", "介绍一下", "有什么功能",
)


def _classify_need_tool(text: str) -> bool:
    """判断用户问题是否需要调用工具（查库/查日志/联网/查企业用户）。规则先行，灰度交 LLM。"""
    t = text.strip()
    low = t.lower()
    if any(k in t for k in _TOOL_KEYWORDS):
        return True
    if len(t) <= 24 and any(k in low for k in _SIMPLE_GREETINGS):
        return False
    return _llm_classify_need_tool(t)


def _llm_classify_need_tool(text: str) -> bool:
    """灰度问题：一次轻量 LLM 判断是否需要工具。异常时保守走 ReAct（保证正确性）。

    分类器只输出 YES/NO，故 max_tokens 压到 8 个 token，降低每轮的分类成本。
    """
    try:
        llm = _build_llm(0.0, max_tokens=8)
        r = llm.invoke([
            ("system", "你是问题分类器。判断用户问题是否需要调用工具（查数据库、查日志、联网搜索、查企业/用户/小程序信息等）才能回答。只输出一个词：YES 或 NO。"),
            ("user", text),
        ])
        return _content_to_str(r.content).strip().upper().startswith("YES")
    except Exception:
        return True


def _build_history_messages(history):
    """history: [{ask, answer}, ...] → [(role, content), ...]（供多轮上下文）。"""
    msgs = []
    for h in (history or []):
        if not isinstance(h, dict):
            continue
        ask = h.get("ask") or h.get("q") or h.get("question")
        ans = h.get("answer") or h.get("a")
        if ask:
            msgs.append(("user", str(ask)))
        if ans:
            msgs.append(("assistant", str(ans)))
    return msgs


_SIMPLE_PROMPT = """你是「django项目」的运维助手--小木，服务于公司内部技术平台后台。请简洁、直接、友好地回答用户问题，用中文，Markdown 格式组织内容。"""


def _simple_stream(user_input, user_context="", history=None, request_id=""):
    """简单问题直通：不走 ReAct，直接 LLM 流式回答（秒回）。带墙钟超时。"""
    yield ("status", "thinking")
    rid = request_id or _uuid.uuid4().hex[:12]
    logger.info("[Agent-直通][req=%s] 简单问题: %s", rid, user_input[:80])
    try:
        llm = _build_llm(0.7)
        messages = []
        if user_context:
            messages.append(("system", user_context))
        # 固定 prompt 与时间戳拆成两条：让 _SIMPLE_PROMPT 成为 byte-0 起的稳定前缀，利于 DeepSeek 前缀缓存命中
        messages.append(("system", _SIMPLE_PROMPT))
        messages.append(("system", _now_context()))
        messages.extend(_build_history_messages(history))
        messages.append(("user", user_input))

        # 后台线程跑 llm.stream，主循环带超时读取
        q = _queue.Queue()

        def _run():
            try:
                for chunk in llm.stream(messages):
                    q.put(("chunk", chunk))
            except Exception as e:
                q.put(("err", e))
            finally:
                q.put(("end", None))

        _threading.Thread(target=_run, daemon=True).start()

        deadline = _time.time() + AGENT_TIMEOUT
        last_usage = None
        while True:
            remaining = deadline - _time.time()
            if remaining <= 0:
                logger.warning("[Agent-直通][req=%s] 超时(%ds)，中断", rid, AGENT_TIMEOUT)
                yield ("error", f"处理超时（{AGENT_TIMEOUT} 秒），请简化问题或稍后重试。")
                return
            try:
                item = q.get(timeout=remaining)
            except _queue.Empty:
                logger.warning("[Agent-直通][req=%s] 超时(%ds)，中断", rid, AGENT_TIMEOUT)
                yield ("error", f"处理超时（{AGENT_TIMEOUT} 秒），请简化问题或稍后重试。")
                return
            kind = item[0]
            if kind == "end":
                break
            if kind == "err":
                raise item[1]
            chunk = item[1]
            u = getattr(chunk, "usage_metadata", None)
            if u:
                last_usage = u
            text = _content_to_str(getattr(chunk, "content", ""))
            if text:
                yield ("text", text)
    except Exception as e:
        logger.error("[Agent-直通][req=%s] 异常: %s", rid, e)
        yield ("error", _translate_error(e, False))
        return
    _log_usage(rid, last_usage)
    logger.info("[Agent-直通][req=%s] 处理完成", rid)
    yield ("done", "")


def _react_stream(user_input, user_context="", history=None, request_id=""):
    """ReAct agent 流式执行（需要工具的问题走这里）。带步数上限 + 墙钟超时。"""
    yield ("status", "thinking")
    rid = request_id or _uuid.uuid4().hex[:12]
    logger.info("[Agent][req=%s] 开始处理: %s", rid, user_input[:80])
    try:
        agent = _get_agent()
        messages = []
        if user_context:
            messages.append(("system", user_context))
        messages.append(("system", _now_context()))
        messages.extend(_build_history_messages(history))
        messages.append(("user", user_input))

        # 后台线程跑 agent.stream，主循环用 queue 带超时读取 → 实现整体墙钟超时
        q = _queue.Queue()

        def _run():
            try:
                for chunk, _metadata in agent.stream(
                    {"messages": messages},
                    stream_mode="messages",
                    config={"recursion_limit": MAX_STEPS},
                ):
                    q.put(("chunk", chunk))
            except Exception as e:
                q.put(("err", e))
            finally:
                q.put(("end", None))

        _threading.Thread(target=_run, daemon=True).start()

        # stream_mode="messages"：LLM 逐 token 流式 + 工具消息，避免回答一次性返回
        pending_calls = {}   # 工具调用 index -> {"name":..., "args": 累积的 JSON 字符串}
        tool_called = False  # 是否已发出过工具调用（用于区分"铺垫"与"直接回答"）
        tool_finished = False  # 工具是否已返回（此后才是最终答案，可流式输出）
        pre_tool_text = []   # 工具调用前的铺垫文字（"我来帮您查询…"），会被丢弃
        last_usage = None    # 最后一个 AIMessageChunk 的 usage_metadata（token 用量）

        deadline = _time.time() + AGENT_TIMEOUT
        while True:
            remaining = deadline - _time.time()
            if remaining <= 0:
                logger.warning("[Agent][req=%s] 超时(%ds)，中断", rid, AGENT_TIMEOUT)
                yield ("error", f"处理超时（{AGENT_TIMEOUT} 秒），请简化问题或稍后重试。")
                return
            try:
                item = q.get(timeout=remaining)
            except _queue.Empty:
                logger.warning("[Agent][req=%s] 超时(%ds)，中断", rid, AGENT_TIMEOUT)
                yield ("error", f"处理超时（{AGENT_TIMEOUT} 秒），请简化问题或稍后重试。")
                return
            kind = item[0]
            if kind == "end":
                break
            if kind == "err":
                raise item[1]

            chunk = item[1]
            u = getattr(chunk, "usage_metadata", None)
            if u:
                last_usage = u
            is_tool = getattr(chunk, "type", "") == "tool"

            if is_tool:
                # 3) 工具返回（ToolMessage）—— 先补发对应 tool_call 日志，再发结果
                for _idx, e in pending_calls.items():
                    try:
                        args_obj = json.loads(e["args"]) if e["args"].strip() else {}
                    except Exception:
                        args_obj = e["args"]
                    logger.info("[Agent][req=%s] 调用工具 %s 入参: %s", rid, e["name"], json.dumps(args_obj, ensure_ascii=False, default=str)[:500])
                    yield ("log", json.dumps({"step": "tool_call", "tool": e["name"], "args": args_obj}, ensure_ascii=False, default=str))
                pending_calls.clear()
                pre_tool_text.clear()  # 丢弃工具调用前的铺垫文字
                tool_finished = True
                name = getattr(chunk, "name", "工具")
                result = _content_to_str(getattr(chunk, "content", ""))
                # 解析工具 JSON 包装，记录 ok 状态（区分「调用成功」与「执行失败」）
                ok = None
                try:
                    ok = json.loads(result).get("ok")
                except Exception:
                    ok = None
                logger.info("[Agent][req=%s] 工具 %s 返回(ok=%s): %s", rid, name, ok, result[:500])
                yield ("log", json.dumps({"step": "tool_result", "tool": name, "ok": ok, "result": result[:800]}, ensure_ascii=False, default=str))
            else:
                # 2) 工具调用（真实字段是 tool_call_chunks：args 为 JSON 字符串分片，按 index 累积）
                for tc in (getattr(chunk, "tool_call_chunks", None) or []):
                    if isinstance(tc, dict):
                        idx = tc.get("index", 0)
                        entry = pending_calls.setdefault(idx, {"name": "", "args": ""})
                        if tc.get("name"):
                            entry["name"] = tc["name"]
                        if tc.get("args"):
                            entry["args"] += tc["args"]
                        tool_called = True
                        tool_finished = False  # 新一轮工具调用开始，其前的文字仍是铺垫
                        pre_tool_text.clear()  # 确认前面的文字是铺垫，丢弃

                # 1) LLM 内容 —— 仅工具返回后的内容才是最终答案，逐 token 流式
                content = getattr(chunk, "content", "")
                if content:
                    text = _content_to_str(content)
                    if text:
                        if tool_finished:
                            yield ("text", text)
                        else:
                            pre_tool_text.append(text)  # 缓冲铺垫（之后有工具调用则丢弃）

        # 全程未调用工具 → 说明是"不调工具的直接回答"，把缓冲的文字补发
        if not tool_called and pre_tool_text:
            yield ("text", "".join(pre_tool_text))
    except Exception as e:
        logger.error("[Agent][req=%s] 处理异常: %s", rid, e)
        yield ("error", _translate_error(e, False))
        return
    _log_usage(rid, last_usage)
    logger.info("[Agent][req=%s] 处理完成", rid)
    yield ("done", "")


def agent_stream(user_input: str, user_context: str = "", history=None, request_id: str = ""):
    """Agent 流式执行。yield (evt_type, content) 元组，与 ai_xfxh.ask_stream 对齐。

    user_context: 可选，注入当前登录用户等上下文（作为 system 消息，不影响落库的 ask）。
    history: 可选，多轮上下文 [{ask, answer}, ...]，按时间先后传入。
    request_id: 可选，外部传入的关联 ID（用于与视图层 chat_id/uid 串起来排查）。
    evt_type:
      - "status"   阶段提示（thinking）
      - "log"      执行日志（JSON 字符串，含工具调用入参/返回结果）
      - "text"     最终回答文本（逐 token 流式）
      - "error"    异常
      - "done"     结束

    简单问题（无需工具）走直通路径秒回；需要工具的问题走 ReAct。
    """
    rid = request_id or _uuid.uuid4().hex[:12]
    need_tool = _classify_need_tool(user_input)
    start = _time.time()
    logger.info(
        "[Agent][req=%s] 入口 need_tool=%s history=%d 提问: %s",
        rid, need_tool, len(history or []), user_input[:80],
    )
    tool_called = False
    had_error = False
    try:
        gen = _react_stream(user_input, user_context, history, rid) if need_tool \
            else _simple_stream(user_input, user_context, history, rid)
        for evt in gen:
            if evt[0] == "log":
                try:
                    if json.loads(evt[1]).get("step") == "tool_call":
                        tool_called = True
                except Exception:
                    pass
            elif evt[0] == "error":
                had_error = True
            yield evt
    finally:
        logger.info(
            "[Agent][req=%s] 结束 latency=%.2fs need_tool=%s tool_called=%s error=%s",
            rid, _time.time() - start, need_tool, tool_called, had_error,
        )
