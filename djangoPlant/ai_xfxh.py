import json, hashlib
from datetime import datetime
import requests
from typing import Generator
from django.core.cache import cache  # type: ignore
from. import Colors as cs
import logging

logger = logging.getLogger(__name__)

# Serper.dev Google 搜索（2500次/月）
SERPER_API_KEY = "f42d69319100e6fb4e9fadcf21791c390365ae69"

# DeepSeek — 纯文本（快）
DS_API_KEY = "sk-6b682ff3567a4ed993b42994fa666eff"
DS_BASE_URL = "https://api.deepseek.com/v1"
DS_MODEL = "deepseek-v4-flash"
# v4-flash 默认开启思考模式（reasoning），非思考用途需显式关闭；此处作为 DeepSeek 通用 extra_body 模板
DS_THINKING_OFF = {"thinking": {"type": "disabled"}}

# 智谱 GLM — 视觉模型 / 图像生成
SF_API_KEY = "ad81015064db4412a4457307b35a1553.YmilED1rUwp4p8Fc"
SF_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
SF_MODEL = "glm-4v-flash"


def getctime():
    c_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return c_time


# ═══════════════════════════════════════════════════════════
#  Serper.dev Google 搜索（带 Redis 缓存）
# ═══════════════════════════════════════════════════════════

_SEARCH_CACHE_TTL = 300  # 5 分钟


def search_web(query: str) -> str:
    """Google 搜索 (Serper.dev) — <2s。异常时抛出明确错误。"""
    cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}"
    cached = cache.get(cache_key)
    if cached:
        logger.info("[搜索] 命中缓存: %s", query[:30])
        return cached

    try:
        resp = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": query, "gl": "cn", "hl": "zh-cn", "num": 8},
            timeout=10,
        )
        if resp.status_code == 403:
            return "【Serper 搜索】API Key 无效或已过期。检查: serper.dev → API Keys。"
        if resp.status_code == 429:
            return "【Serper 搜索】今日免费额度(2,500次)已用完，请明天再试或升级套餐。"
        if resp.status_code != 200:
            return f"【Serper 搜索】返回异常 HTTP {resp.status_code}，请稍后重试。"

        data = resp.json()
        results = []
        for item in data.get("organic", [])[:8]:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            date = item.get("date", "")
            parts = [title]
            if date:
                parts.append(f"({date})")
            parts.append(snippet)
            results.append(" | ".join(parts))

        text = "\n\n".join(results)[:3000]
        if text:
            cache.set(cache_key, text, _SEARCH_CACHE_TTL)
            logger.info("[Serper] 搜索完成: %s 字符", len(text))
            return text
        return "【Serper 搜索】无匹配结果。"
    except requests.Timeout:
        logger.warning("[Serper] 超时")
        return "【Serper 搜索】请求超时(10s)，Google 搜索服务暂时不可达，请稍后重试。"
    except Exception as e:
        logger.error("[Serper] 搜索异常: %s", e)
        return f"【Serper 搜索】网络异常或服务不可用。错误: {str(e)[:150]}"


# ═══════════════════════════════════════════════════════════
#  关键词意图分类
# ═══════════════════════════════════════════════════════════

_SEARCH_KEYWORDS = [
    "最新", "今天", "今日", "现在", "当前", "实时", "刚刚", "最近",
    "新闻", "天气", "股价", "股票", "台风", "地震", "比赛", "比分",
    "热搜", "发生了什么", "热点", "疫情", "发布会", "公告",
    "今天几号", "今天星期几", "几点了", "现在几点",
    "多少钱", "价格", "汇率", "最新消息",
    "上映", "票房", "电影", "首播", "直播",
]


def _needs_search(prompt: str) -> bool:
    text = prompt.strip()
    for kw in _SEARCH_KEYWORDS:
        if kw in text:
            return True
    return False


# ═══════════════════════════════════════════════════════════
#  SparkChatClient — 直接 LLM 流式 + 搜索 + 上下文记忆
# ═══════════════════════════════════════════════════════════

# langchain 懒加载 — 首次调用才 import，避免拖慢 Django 启动/重载
_chat_openai = None
_system_msg = None
_human_msg = None
_ai_msg = None


def _get_chat_classes():
    global _chat_openai, _system_msg, _human_msg, _ai_msg
    if _chat_openai is None:
        from langchain_openai import ChatOpenAI as _ChatOpenAI  # type: ignore
        from langchain_core.messages import SystemMessage as _SM  # type: ignore
        from langchain_core.messages import HumanMessage as _HM     # type: ignore
        from langchain_core.messages import AIMessage as _AM        # type: ignore
        _chat_openai = _ChatOpenAI
        _system_msg = _SM
        _human_msg = _HM
        _ai_msg = _AM
    return _chat_openai, _system_msg, _human_msg, _ai_msg


def prewarm():
    """启动预热：后台线程预加载 langchain。每个进程生命周期内只执行一次。"""
    import threading, os
    if _get_chat_classes.__dict__.get('__prewarmed'):
        return
    _get_chat_classes.__dict__['__prewarmed'] = True

    def _warm():
        logger.info("🔥 预热开始…")
        import time as _t; t0 = _t.time()
        _get_chat_classes()
        logger.info("🔥 预热完成 +%.1fs", _t.time() - t0)
    threading.Thread(target=_warm, daemon=True).start()

SYSTEM_PROMPT = """你是AI助手。当前时间是{now}。请用中文精准且清晰地回答问题，使用 Markdown 格式组织内容。
{search_context}
当涉及技术问题时，提供代码示例和分步说明。当涉及分析问题时，提供多角度观点。
如果用户的问题与之前的对话相关，请结合上下文进行连贯回答。上下文中提到过的事物，直接用代词或简称即可，不要装作不知道。
【硬规则】当上方提供了搜索结果时，你必须基于搜索结果回答用户的问题，严禁回复"无法获取""搜索不可用""没有实时能力"等说法。搜索结果就是为你查询到的实时信息，直接用即可。"""

# ═══════════════════════════════════════════════════════════
#  异常翻译 — 把底层报错翻译成清晰的用户提示
# ═══════════════════════════════════════════════════════════

def _translate_error(err: Exception, has_image: bool) -> str:
    """把 API 报错翻译成中文，明确指出哪个环节出了什么问题"""
    raw = str(err)
    low = raw.lower()

    # ── 429 并发 / 频率限制 ──
    if "429" in raw or "rate" in low or "too many" in low:
        if has_image:
            return "【智谱 GLM-4V】请求太频繁，请稍等几秒再试。检查: 智谱控制台 → 查看 QPS 限制。"
        return "【DeepSeek】请求太频繁，请稍等几秒再试。"

    # ── 401 / 403 认证失败 ──
    if "401" in raw or "unauthorized" in low:
        if has_image:
            return "【智谱 GLM-4V】API Key 认证失败，可能已过期或被禁用。检查: open.bigmodel.cn → API 密钥管理。"
        return "【DeepSeek】API Key 认证失败，可能已过期或被禁用。检查: platform.deepseek.com → API Keys。"

    if "403" in raw or "forbidden" in low or "disabled" in low:
        if has_image:
            return "【智谱 GLM-4V】访问被拒绝，可能是该模型未开通或已下线。检查: open.bigmodel.cn → 模型广场。"
        return "【DeepSeek】访问被拒绝，可能是余额不足或该模型未开通。"

    # ── 402 / insufficient balance ──
    if "402" in raw or "insufficient" in low or "balance" in low:
        if has_image:
            return "【智谱 GLM-4V】账户余额不足。请前往 open.bigmodel.cn 充值或等待免费额度重置。"
        return "【DeepSeek】账户余额不足。请前往 platform.deepseek.com 充值。"

    # ── 超时 ──
    if "timeout" in low or "timed out" in low:
        if has_image:
            return "【智谱 GLM-4V】响应超时，图片可能过大或网络不稳定。建议压缩图片后重试。"
        return "【DeepSeek】响应超时，网络波动或服务繁忙，请重试。"

    # ── image 格式错误 ──
    if "image" in low and ("invalid" in low or "size" in low or "format" in low or "height" in low or "width" in low):
        return "【智谱 GLM-4V】图片格式或尺寸不符合要求。建议使用 JPG/PNG、分辨率 ≥28x28、大小 ≤5MB。"

    # ── model not found ──
    if "model" in low and ("not found" in low or "unavailable" in low):
        model_id = SF_MODEL if has_image else DS_MODEL
        provider = "智谱" if has_image else "DeepSeek"
        return f"【{provider}】模型 {model_id} 不存在或已下线。检查控制台当前可用模型列表。"

    # ── 最后兜底：带上关键信息 ──
    if has_image:
        return f"【智谱 GLM-4V】调用异常。错误详情: {raw[:300]}"
    return f"【DeepSeek】调用异常。错误详情: {raw[:300]}"


class SparkChatClient:
    """AI 对话客户端 — 文字用 DeepSeek，图片用智谱 GLM-4V。双模型自动切换。
    首次调用时才初始化 LLM 客户端，避免拖慢 Django 启动。
    """

    def __init__(self):
        self._llm = None           # 文字模型 — 首次调用时懒加载
        self._vision_llm = None    # 视觉模型 — 首次调用时懒加载
        self._histories: dict = {}
        self._max_history = 6

    def _ensure_llms(self):
        """懒加载 LLM 客户端（首次调用才 import langchain + 创建实例）"""
        if self._llm is None:
            _ChatOpenAI, _, _, _ = _get_chat_classes()
            self._llm = _ChatOpenAI(
                model=DS_MODEL, api_key=DS_API_KEY, base_url=DS_BASE_URL,
                temperature=0.7, max_tokens=2048,
                extra_body=DS_THINKING_OFF,  # v4-flash 关闭思考，等价 deepseek-chat 非思考行为
            )
            self._vision_llm = _ChatOpenAI(
                model=SF_MODEL, api_key=SF_API_KEY, base_url=SF_BASE_URL,
                temperature=0.2, max_tokens=4096,
            )

    def ask_stream(self, prompt: str, session_id: str = "default", image: str = None) -> Generator:
        """流式调用。图片：分两步走 — ①视觉模型提取文字 → ②文字模型结合原文回答。"""
        import time as _time
        t_total = _time.time()
        has_image = bool(image)

        def _log(msg):
            elapsed = _time.time() - t_total
            marker = "🖼" if has_image else "📝"
            logger.info("%s [+%.1fs] %s", marker, elapsed, msg)

        _log(f"请求: {prompt[:80]}")

        yield ("status", "preparing")
        self._ensure_llms()
        _, SystemMessage, HumanMessage, AIMessage = _get_chat_classes()

        # ② 搜索
        search_text = ""
        if _needs_search(prompt) and not has_image:
            yield ("status", "searching")
            t0 = _time.time()
            search_text = search_web(prompt)
            _log(f"搜索耗时: +{_time.time()-t0:.1f}s 结果{len(search_text)}字符")
            if search_text and not search_text.startswith("搜索"):
                yield ("search_result", search_text[:800])
        elif not has_image:
            yield ("status", "thinking")

        # ③ 构建消息
        now = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        _sc_hint = (
            '\n\n【以下是系统为你查询到的实时信息，你必须基于这些信息回答用户问题。'
            '禁止说「无法获取」「搜索不可用」——信息已经查到了，直接用！'
            '用自然语言重新组织，不要照搬原文。】\n'
        )
        sc = f"{_sc_hint}{search_text}" if search_text else ""
        system_content = SYSTEM_PROMPT.format(now=now, search_context=sc)
        messages = [SystemMessage(content=system_content)]

        history = self._histories.get(session_id, [])
        for h in history[-self._max_history:]:
            messages.append(HumanMessage(content=h["user"]))
            messages.append(AIMessage(content=h["assistant"]))

        if has_image:
            # ── 步骤①：视觉模型提取图片文字 ──
            yield ("status", "extracting")
            image_url = image if (image.startswith("http://") or image.startswith("https://")) else f"data:image/jpeg;base64,{image}"
            _log("视觉提取开始…")
            t0 = _time.time()
            extracted = ""
            try:
                ocr_msg = HumanMessage(content=[
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": "请只输出图片中的所有文字内容。不要加任何解释、前缀或后缀。如果图片没有文字，输出[无文字]。"},
                ])
                ocr_resp = self._vision_llm.invoke([ocr_msg])
                extracted = ocr_resp.content.strip() if hasattr(ocr_resp, 'content') else str(ocr_resp).strip()
                _log(f"视觉提取完成 +{_time.time()-t0:.1f}s: {extracted[:100]}")
            except Exception as e:
                _log(f"视觉提取失败: {e}")
                extracted = "[提取失败]"

            # ── 步骤②：文字模型结合提取结果回答 ──
            yield ("status", "analyzing")
            has_text = extracted and extracted != "[无文字]" and extracted != "[提取失败]"
            if has_text:
                prompt_with_context = (
                    f"【图片中提取到的文字内容】\n{extracted}\n\n"
                    f"【用户问题】{prompt}\n\n"
                    f"请基于上面的文字内容回答用户问题。如果问题要求翻译，请给出翻译；"
                    f"如果问题要求分析，请基于文字进行分析；如果只是提问，请用中文回答。"
                )
            else:
                # 图片无文字 → 可以补充一句，但不要编造
                prompt_with_context = (
                    f"【用户上传了一张图片】\n"
                    f"【用户问题】{prompt}\n\n"
                    f"如果用户问的是图片里有什么，请说明：图片中没有文字内容，你可以尝试让用户用文字描述图片。"
                    f"如果用户问的是其他问题，请直接回答。"
                )
            _log(f"文字模型回答: prompt={len(prompt_with_context)}字符")
            messages.append(HumanMessage(content=prompt_with_context))
        else:
            messages.append(HumanMessage(content=prompt))

        # ④ LLM 流式生成（有图片时视觉模型已完成提取，文字模型负责回答）
        yield ("status", "generating")
        llm = self._llm
        _log(f"开始 LLM 调用: {DS_MODEL}")

        full = ""
        first_token = True
        t_stream_start = _time.time()
        try:
            for chunk in llm.stream(messages):
                content = chunk.content if hasattr(chunk, "content") else str(chunk)
                if content:
                    if first_token:
                        first_token = False
                        _log(f"首个 token 到达 (+{_time.time()-t_stream_start:.1f}s)")
                    full += content
                    yield ("text", content)
        except Exception as e:
            err_msg = _translate_error(e, has_image)
            _log(f"❌ 错误: {err_msg}")
            yield ("error", err_msg)
            return

        t_stream = _time.time() - t_stream_start
        tps = len(full) / t_stream if t_stream > 0 else 0
        _log(f"LLM 完成: {len(full)} 字符, 总耗时 {t_stream:.1f}s, 速度 {tps:.0f} 字符/秒")

        # ⑤ 存档上下文
        history.append({"user": prompt, "assistant": full})
        if len(history) > 10:
            history = history[-10:]
        self._histories[session_id] = history

        yield ("done", "")
        _log(f"✅ 全部完成, 总计 +{_time.time()-t_total:.1f}s")
