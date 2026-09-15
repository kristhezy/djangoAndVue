"""菜单注册表 —— 侧边栏菜单项的唯一写死点。

菜单项本身(图标/URL/分组)仍写在 templates/partials/sidebar.html，
这里只登记「菜单 key → URL」的映射，同时服务两件事：
1. 渲染判断：`menus|has_menu:'soon'` 用 key 判断是否显示
2. 拦截判断：MenuPermissionMiddleware 拿 request.path 反查 key 是否有权限

要新增一个角色、调整某个角色能看哪些菜单，直接改数据库的 role / role_menu 表，
不用动这个文件。只有当「新增一个菜单项」时才需要在这里加一行 key。
"""

# 菜单 key → 页面 URL（与 sidebar.html 里 href 一一对应）
MENU_MAP = {
    # 公共菜单（所有角色默认可见）
    'home': '/home',
    'mmeett': '/ov/mmeettopen',
    # 管理员菜单
    'other': '/pv/other',
    'soon': '/ov/soonConfig',
    'setting': '/ov/setting',
    'twCompSet': '/ov/twCompSet',
    # SAAS企业开户配置（分组）
    'jtSaleskits': '/sv/jtSaleskits',
    'hwskset': '/sv/hwskset',
    'upgradeR3': '/sv/upgradeR3',
    'basicComp': '/sv/basicComp',
    'baseUpgradeSK': '/sv/baseUpgradeSK',
    # 独立菜单
    'updateCI': '/sv/updateCT',
    'companyModule': '/sv/companyModule',
    # SAAS辅助工具（分组）
    'delCP': '/sv/delCP',
    'forWeCom': '/sv/forWeCom',
    'mergeUser': '/sv/mergeUser',
    'delBindRelation': '/sv/delBindRelation',
    'aboutLogin': '/sv/queryLoginCode',
    'dzFunction': '/sv/dzFunction',
    'batchDeleteClue': '/sv/batchDeleteClue',
    # 其余独立菜单
    'afterSales': '/sv/afterSales',
    'miniprogram': '/sv/miniprogram',
    'mynote': '/pv/mynote',
    'usercenter': '/pv/usercenter',
    'easyIC': '/pv/easyIC',
    'aitools': '/pv/aitools',
    'agent': '/pv/agent',
    'radar': '/radar',
}

# 公共菜单 key（种子数据里给 user 角色默认配的，也是「非管理员也可见」的定义）
PUBLIC_MENUS = {'home', 'mmeett'}

# 管理员菜单 key = 全部 - 公共
ADMIN_MENUS = set(MENU_MAP) - PUBLIC_MENUS


def match_menu_key(path):
    """按请求 path 反查菜单 key。

    返回 (menu_key, matched) —— 只有精确等于 或 以 value + '/' 开头才算命中，
    避免 /home 误伤 /homexxx。未命中返回 (None, False)。
    """
    for key, url in MENU_MAP.items():
        if path == url or path.startswith(url + '/'):
            return key, True
    return None, False
