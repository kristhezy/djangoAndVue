""" 网站公共文本配置文件 """
import os, time

# 静态文件版本 — 基于文件自身 mtime，只在真正变更时变
_STATIC_VERSION = None

def _get_static_version():
    global _STATIC_VERSION
    if _STATIC_VERSION is None:
        try:
            _STATIC_VERSION = str(int(os.path.getmtime(__file__)))
        except OSError:
            _STATIC_VERSION = str(int(time.time()))
    return _STATIC_VERSION

# ============================================================
# 图标配置（FontAwesome 6）
# 格式: 'KEY': 完整的 <i> 标签
# 后续统一在此修改图标，模板中直接通过 {{ icons.xxx }} 输出
# ============================================================
ICONS = {
    # ---- base.html 头部 & 菜单 ----
    'HEADER_LOGO': '<i class="fa-brands fa-nfc-symbol"></i>',
    'LOGOUT': '<i class="fa-solid fa-right-from-bracket"></i>',
    'HOME': '<i class="fa-solid fa-house"></i>',
    'OTHER': '<i class="fa-solid fa-sheet-plastic"></i>',
    'SOON_CONFIG': '<i class="fa-brands fa-squarespace"></i>',
    'MMEETT_OPEN': '<i class="fa-brands fa-mix"></i>',
    'XCARD_CONFIG': '<i class="fa-brands fa-xing"></i>',
    'ORIGIN_SETTING': '<i class="fa-solid fa-arrows-to-dot"></i>',
    'TW_COMP_SET': '<i class="fa-solid fa-won-sign"></i>',
    'BARS_PROGRESS': '<i class="fa-solid fa-bars-progress"></i>',
    'ARROW_DOWN': '<i class="fa-solid fa-chevron-down arrow"></i>',
    'PEN_TO_SQUARE': '<i class="fa-solid fa-pen-to-square"></i>',
    'LIST_UL': '<i class="fa-solid fa-list-ul"></i>',
    'HAMMER': '<i class="fa-solid fa-hammer"></i>',
    'UNIVERSAL_ACCESS': '<i class="fa-solid fa-universal-access"></i>',
    'COMMENTS': '<i class="fa-solid fa-comments"></i>',
    'LIST': '<i class="fa-solid fa-list"></i>',
    'USER': '<i class="fa-solid fa-user"></i>',
    'ARROW_LEFT_RIGHT': '<i class="fa-solid fa-arrow-right-arrow-left"></i>',
    'MINI_PROGRAM': '<i class="fa-solid fa-litecoin-sign"></i>',
    'MY_NOTE': '<i class="fa-solid fa-list"></i>',
    'FOR_WECOM': '<i class="fa-solid fa-comments"></i>',
    'LINODE':'<i class="fa-brands fa-linode"></i>',

    # ---- MmeettOpen.html ----
    'SISTRIX': '<i class="fa-brands fa-sistrix"></i>',

    # ---- 通用 ----
    'PLUS': '<i class="fa-solid fa-plus"></i>',
    'TRASH': '<i class="fa-solid fa-trash-can"></i>',
    'PLAY': '<i class="fa-solid fa-play"></i>',
    'COPY': '<i class="fa-solid fa-copy"></i>',
    'XMARK': '<i class="fa-solid fa-xmark"></i>',
    'CLOCK': '<i class="fa-solid fa-clock-rotate-left"></i>',
    'PAPER_PLANE': '<i class="fa-solid fa-paper-plane"></i>',
    'ANGLE_UP': '<i class="fa-solid fa-angle-up"></i>',
    'CIRCLE_WARN': '<i class="fa-solid fa-circle-exclamation"></i>',
    'TRIANGLE_WARN': '<i class="fa-solid fa-triangle-exclamation"></i>',
    'RIBBON': '<i class="fa-solid fa-ribbon"></i>',
    'SEEDLING': '<i class="fa-solid fa-seedling"></i>',
    'EDGE_LEGACY': '<i class="fa-brands fa-edge-legacy"></i>',
    'QUINSCAPE': '<i class="fa-brands fa-quinscape"></i>',
    'UIKIT': '<i class="fa-brands fa-uikit"></i>',
}

SITE_CONFIG = {
    # 静态文件版本号，基于文件 mtime（只在真变更时变，不破坏浏览器缓存）
    'STATIC_VERSION': _get_static_version(),
    #菜单文本
    'SITE_HOME':'/home',
    'SITE_HOME_NAME':'AT-首页',
    'SITE_OTHER':'/pv/other',
    'SITE_OTHER_NAME':'操作变更记录',
    'TITLE_SOON':'Soon版开户&配置',
    'SITE_SOONCONFIG':'/ov/soonConfig',
    'SITE_SOONCONFIG_NAME':'Soon版开户&配置',
    'SITE_MMEETTOPEN':'/ov/mmeettopen',
    'SITE_MMEETTOPEN_NAME':'Mmeett开户&配置',
    'SITE_XCARDCONFIG':'/ov/xcard',
    'SITE_XCARDCONFIG_NAME':'XCard开户&配置',
    'SITE_SETTING':'/ov/setting',
    'SITE_SETTING_NAME':'基线版开户&配置',
    'SITE_TWCOMPSET':'/ov/twCompSet',
    'SITE_TWCOMPSET_NAME':'通威版开户&配置',
    'TITLE_COMPCONFIG':'SAAS企业开户配置',
    'SITE_JTSK':'/sv/jtSaleskits',
    'SITE_JTSK_NAME':'加推Saleskits',
    'SITE_HWSKSET':'/sv/hwskset',
    'SITE_HWSKSET_NAME':'华为云SK配置',
    'SITE_UPGRADER3':'/sv/upgradeR3',
    'SITE_UPGRADER3_NAME':'转介绍3.0配置',
    'SITE_BASICCOMP':'/sv/basicComp',
    'SITE_BASICCOMP_NAME':'销售工具版配置',
    'SITE_BASEUPGSK':'/sv/baseUpgradeSK',
    'SITE_BASEUPGSK_NAME':'工具版升级SK',
    'SITE_UPDATECI':'/sv/updateCT',
    'SITE_UPDATECI_NAME':'修改SAAS企业信息',
    'SITE_COMPMODULE':'/sv/companyModule',
    'SITE_COMPMODULE_NAME':'配置SAAS企业模块',
    'TITLE_TOOLS':'SAAS辅助工具',
    'SITE_DELCP':'/sv/delCP',
    'SITE_DELCP_NAME':'删除线索[合]',
    'SITE_FORWECOM':'/sv/forWeCom',
    'SITE_FORWECOM_NAME':'企业微信相关',
    'SITE_MERGEUSER':'/sv/mergeUser',
    'SITE_MERGEUSER_NAME':'手工合并用户',
    'SITE_DELBINDRLT':'/sv/delBindRelation',
    'SITE_DELBINDRLT_NAME':'解除绑定关系',
    'SITE_ABOUTLOGIN':'/sv/queryLoginCode',
    'SITE_ABOUTLOGIN_NAME':'登录验证相关',
    'SITE_DINGZHI':'/sv/dzFunction',
    'SITE_DINGZHI_NAME':'定制企业功能',
    'SITE_BATCHDC':'/sv/batchDeleteClue',
    'SITE_BATCHDC_NAME':'批量删除线索',
    'SITE_AFTERSALES':'/sv/afterSales',
    'SITE_AFTERSALES_NAME':'AfterSales(SAAS)',
    'SITE_MINIPROGRAM':'/sv/miniprogram',
    'SITE_MINIPROGRAM_NAME':'工具版小程序发版',
    'SITE_MYNOTE':'/pv/mynote',
    'SITE_MYNOTE_NAME':'我的记录',
    'SITE_USERCENTER':'/pv/usercenter',
    'SITE_USERCENTER_NAME':'用户中心',
    'SITE_EASYIC':'/pv/easyIC',
    'SITE_EASYIC_NAME':'接口灵活调用',
    'SITE_AITOOLS':'/pv/aitools',
    'SITE_AITOOLS_NAME':'my AIChat',
    'SITE_AGENT':'/pv/agent',
    'SITE_AGENT_NAME':'my Agent',
    'SITE_RADAR':'/pv/radar',
    'SITE_RADAR_NAME':'SAAS企业雷达数据',

    #文本
}