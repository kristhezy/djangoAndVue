"""
URL configuration for djangoPlant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin  # type: ignore
from django.urls import path, re_path  # type: ignore
from. import originview as ov, publicview as pv, saasview as sv, userlogin as ul, miniprogram
from. import spa

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login',ul.user_login,name="login"),
    path('logout',ul.user_logout,name="logout"),
    path('denied',pv.denied,name="denied"),
    #publicview
    path('',spa.spa_index,name="home"),
    path('home',pv.home,name="home"),
    path('pv/other',pv.other,name='other'),
    path('pv/pagecount',pv.pagecount,name='pagecount'),
    path('pv/other/<str:part>',pv.other_part,name='otherpart'),
    path('pv/mynote',pv.gmynote,name='mynote'),
    path('pv/mynote/<str:opration>',pv.pmynote,name='mynoteopration'),
    path('pv/usercenter',pv.gusercenter,name='usercenter'),
    path('pv/usercenter/<str:uctype>',pv.usercenter,name='usercenteructype'),
    path('pv/registTP',pv.registTP,name='usercenter'),
    path('pv/easyIC',pv.easyIC,name='easyIC'),
    path('pv/aitools',pv.aitools,name='aitools'),
    path('pv/aitools/stream',pv.aitools_stream,name='aitoolsStream'),
    path('pv/aitools/<str:ptype>',pv.paitools,name='aitoolsPost'),
    path('pv/agent',pv.agent,name='agent'),
    path('pv/agent/float',pv.agent_float,name='agentFloat'),
    path('pv/agent/stream',pv.agent_stream,name='agentStream'),
    path('pv/agent/history',pv.agent_history,name='agentHistory'),
    #originview
    path('ov/soonConfig',ov.soonConfig),
    path('ov/mmeettopen',ov.mmeettopen),
    path('ov/mmeettTreeView',ov.mmeettTreeView),
    path('ov/pmmeettTreeData',ov.pmmeettTreeData),
    path('ov/pmmeett/<str:action>',ov.pmmeett_action),
    path('ov/pmmeettTreeChildren',ov.pmmeettTreeChildren),
    # 暂禁用 XCard 页面
    # path('ov/xcard', ov.page_404),
    # path('ov/xcard/<str:action>', ov.page_404),
    path('ov/setting',ov.setting),
    path('ov/setting/<str:action>',ov.setting_action),
    path('ov/twCompSet',ov.twCompSet),
    #saasview
    path('sv/upgradeR3',sv.upgradeR3),
    path('sv/basicComp',sv.basicCompCfg),
    path('sv/hwskset',sv.hwskset),
    path('sv/jtSaleskits',sv.jtSaleskits),
    path('sv/baseUpgradeSK',sv.baseUpgradeSK),
    path('sv/updateCT',sv.updateCT),
    path('sv/updateCInfo',sv.updateCInfo),
    path('sv/companyModule',sv.companyModule),
    path('sv/removeTagTel',sv.removeTagTel),
    path('sv/delclueinfo',sv.delclueinfo),
    path('sv/delCP',sv.delCP),
    path('sv/queryuibycp',sv.queryuibycp),
    path('sv/batchDeleteClue',sv.batchDeleteClue),
    path('sv/saci',sv.saci),
    path('sv/splc',sv.splc),
    path('sv/forWeCom',sv.forWechatCom),
    path('sv/mergeUser',sv.mergeUser),
    path('sv/delBindRelation',sv.delBindRelation),
    path('sv/cleanAppToken',sv.cleanAppToken),
path('sv/queryLoginCode',sv.queryLoginCode),
    path('sv/dzFunction',sv.dzFunction),
    path('sv/afterSales',sv.afterSales),
    path('sv/querycompid/<str:sysvs>',sv.queryCompanyId),
    path('sv/queryci',sv.queryCI),
    path('sv/querySCID',sv.querySCID),
    path('sv/queryca',sv.queryCA),
    path('sv/queryaal',sv.queryAAL),
    path('sv/selfcreatedCS',sv.selfcreatedCS),
    path('sv/privset',sv.privset),
    path('sv/dzapplet',sv.dzconfig),
    path('sv/getappid',sv.getappid),
    path('sv/miniprogram',sv.miniprogram),
    path('sv/miniprogramRelease/<str:type>',sv.miniprogramRelease),
    path('sv/queryMiniprogramRecord/<str:type>',sv.queryMiniprogramRecord),
    path('sv/qmbydsan',sv.qmbydsan),
    path('sv/aftergetqmbydsan',sv.aftergetqmbydsan),

    path('download/dynamic/', miniprogram.download_dynamic_file, name='download_dynamic'),
]

# uvicorn 开发模式下提供静态文件（runserver 自动加，uvicorn 需显式配置）
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# SPA 兜底：所有未命中路由交给 Vue index.html（必须放在 static 之后，避免吞掉静态文件）
urlpatterns += [
    re_path(r'^.*$', spa.spa_index, name='spa'),
]

# 自定义 404 页面（仅 DEBUG=False 时生效；开发环境用 @login_required 控制访问）
handler404 = 'djangoPlant.publicview.page_not_found'
