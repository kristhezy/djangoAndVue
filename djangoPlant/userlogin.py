from. import render,redirect,json,JsonResponse,login_required,authenticate,login,logout,HttpResponseRedirect
from.pub_InputAndQuery import InputAndQuery as iaq
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect # type: ignore

@ensure_csrf_cookie
@csrf_protect
def user_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['ln']
        password = data['pw']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            print("用户登录成功！")
            uuid = user.id
            realName = user.last_name
            request.session['isLoggedIn'] = True
            request.session['ln'] = username
            request.session['rn'] = realName
            request.session['uuid'] = uuid
            userInfo = iaq().query_userInfo_byuuid(uuid) or {}
            print("getuserinfo:",userInfo)
            # uid/uname 兜底：auth_user 有账号但 users 无活行时（历史遗留）不再崩
            request.session['uid'] = userInfo.get("id")
            request.session['uname'] = userInfo.get("name") or realName or username
            # mr 改为由 role/user_role 推导（旧 menu_role 语义，99=admin 2=user）
            request.session['mr'] = iaq().query_mr_byuuid(uuid)
            # 菜单权限集合：由 role_menu 推导，供侧边栏显隐 + 中间件拦截使用
            request.session['menus'] = iaq().query_menu_keys_byuuid(uuid)

            # 登录成功后跳转：优先使用前端传来的 next，其次是 session 中保存的，最后默认 /home
            redirect_url = data.get('next', '') or request.session.pop('login_redirect', '') or '/'
            return JsonResponse({
                'success': True,
                'redirect_url': redirect_url
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '用户名或密码错误，或用户已被禁用！'
            })
    else:
        if 'isLoggedIn' in request.session and request.session['isLoggedIn']:
            return redirect('/')
        return render(request, 'login.html')

@login_required
def user_logout(request):
    # 记录来源路径，登录成功后跳回原页面
    referer = request.META.get('HTTP_REFERER', '')
    # 去掉 plain 模式标记和可能的前缀，保留目标页面路径
    referer = referer.replace('?_plain=1','').replace('&_plain=1','')
    login_redirect = referer if referer else '/home'
    logout(request)  # 登出，销毁会话（session 被清空）
    request.session['isLoggedIn'] = False
    request.session['login_redirect'] = login_redirect
    return HttpResponseRedirect('/login')