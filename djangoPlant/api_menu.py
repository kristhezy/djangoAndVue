"""菜单接口：把 sidebar.html 的结构/分组/图标抽成数据，按用户权限过滤返回。

菜单结构唯一权威在此维护（对应 templates/partials/sidebar.html）。
数据结构：STANDS（独立项）+ GROUPS（分组，含 title 与 items）。
"""
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from . import JsonResponse
from .config.text_config import SITE_CONFIG as C

# 图标 class（与 sidebar.html 一致，Vue 侧用 FontAwesome class 渲染）
I = {
    'home': 'fa-solid fa-house',
    'other': 'fa-solid fa-sheet-plastic',
    'soon': 'fa-brands fa-squarespace',
    'mmeett': 'fa-brands fa-mix',
    'setting': 'fa-solid fa-arrows-to-dot',
    'twCompSet': 'fa-solid fa-won-sign',
    'compconfig': 'fa-solid fa-bars-progress',
    'updateCI': 'fa-solid fa-pen-to-square',
    'companyModule': 'fa-solid fa-list-ul',
    'tools': 'fa-solid fa-hammer',
    'afterSales': 'fa-solid fa-comments',
    'miniprogram': 'fa-solid fa-litecoin-sign',
    'mynote': 'fa-solid fa-list',
    'usercenter': 'fa-solid fa-user',
    'easyIC': 'fa-brands fa-linode',
    'aitools': 'fa-brands fa-think-peaks',
    'agent': 'fa-solid fa-robot',
}

# 独立菜单项（按 sidebar 顺序）
STANDS = [
    ('home', C['SITE_HOME'], C['SITE_HOME_NAME']),
    ('other', C['SITE_OTHER'], C['SITE_OTHER_NAME']),
    ('soon', C['SITE_SOONCONFIG'], C['SITE_SOONCONFIG_NAME']),
    ('mmeett', C['SITE_MMEETTOPEN'], C['SITE_MMEETTOPEN_NAME']),
    ('setting', C['SITE_SETTING'], C['SITE_SETTING_NAME']),
    ('twCompSet', C['SITE_TWCOMPSET'], C['SITE_TWCOMPSET_NAME']),
    ('updateCI', C['SITE_UPDATECI'], C['SITE_UPDATECI_NAME']),
    ('companyModule', C['SITE_COMPMODULE'], C['SITE_COMPMODULE_NAME']),
    ('afterSales', C['SITE_AFTERSALES'], C['SITE_AFTERSALES_NAME']),
    ('miniprogram', C['SITE_MINIPROGRAM'], C['SITE_MINIPROGRAM_NAME']),
    ('mynote', C['SITE_MYNOTE'], C['SITE_MYNOTE_NAME']),
    ('usercenter', C['SITE_USERCENTER'], C['SITE_USERCENTER_NAME']),
    ('easyIC', C['SITE_EASYIC'], C['SITE_EASYIC_NAME']),
    ('aitools', C['SITE_AITOOLS'], C['SITE_AITOOLS_NAME']),
    ('agent', C['SITE_AGENT'], C['SITE_AGENT_NAME']),
]

# 分组菜单（title 用 group icon，items 无独立 icon）
GROUPS = [
    ('compconfig', C['TITLE_COMPCONFIG'], [
        ('jtSaleskits', C['SITE_JTSK'], C['SITE_JTSK_NAME']),
        ('hwskset', C['SITE_HWSKSET'], C['SITE_HWSKSET_NAME']),
        ('upgradeR3', C['SITE_UPGRADER3'], C['SITE_UPGRADER3_NAME']),
        ('basicComp', C['SITE_BASICCOMP'], C['SITE_BASICCOMP_NAME']),
        ('baseUpgradeSK', C['SITE_BASEUPGSK'], C['SITE_BASEUPGSK_NAME']),
    ]),
    ('tools', C['TITLE_TOOLS'], [
        ('delCP', C['SITE_DELCP'], C['SITE_DELCP_NAME']),
        ('forWeCom', C['SITE_FORWECOM'], C['SITE_FORWECOM_NAME']),
        ('mergeUser', C['SITE_MERGEUSER'], C['SITE_MERGEUSER_NAME']),
        ('delBindRelation', C['SITE_DELBINDRLT'], C['SITE_DELBINDRLT_NAME']),
        ('aboutLogin', C['SITE_ABOUTLOGIN'], C['SITE_ABOUTLOGIN_NAME']),
        ('dzFunction', C['SITE_DINGZHI'], C['SITE_DINGZHI_NAME']),
        ('batchDeleteClue', C['SITE_BATCHDC'], C['SITE_BATCHDC_NAME']),
    ]),
]


def _item(key, url, title):
    return {'key': key, 'title': title, 'url': url, 'icon': I.get(key, '')}


@login_required
@never_cache
def menu_api(request):
    menus = request.session.get('menus', []) or []
    user = {
        'uid': request.session.get('uid'),
        'uname': request.session.get('uname'),
        'rn': request.session.get('rn'),
    }
    standalone = [_item(k, u, t) for (k, u, t) in STANDS if k in menus]
    groups = []
    for gkey, gtitle, items in GROUPS:
        visible = [_item(k, u, t) for (k, u, t) in items if k in menus]
        if visible:
            groups.append({'key': gkey, 'title': gtitle, 'icon': I.get(gkey, ''), 'items': visible})
    return JsonResponse({'code': '0', 'msg': '成功', 'data': {'user': user, 'groups': groups, 'standalone': standalone}})
