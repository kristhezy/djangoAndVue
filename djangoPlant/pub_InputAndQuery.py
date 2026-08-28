from. import Colors
from.publicDef import publicDef as pd
from datetime import datetime
from django.utils import timezone  # type: ignore
from django.db.models import Q, Count  # type: ignore
from django.db.models.functions import Coalesce  # type: ignore
from mysqlite.models import (
    QGetMessage, User, RequestHistory, AiText,
    MiniprogramRecord, AgentChat, MmeettOpLog,
    MiniprogramCompanyDomainStatus, MiniprogramBindWechat,
    Role, UserRole, RoleMenu,
)
from .menu_registry import PUBLIC_MENUS


class InputAndQuery(object):

    # ---- 工具方法 ----
    @staticmethod
    def _esc(s):
        """字符串安全转义（用于 qm_kw 拼接）"""
        if s is None: return ''
        return str(s).replace("'", "''")

    @staticmethod
    def _esc_int(v, default=0):
        try: return int(v)
        except (ValueError, TypeError): return default

    # ---- ORM → dict 适配器（保持与旧 raw SQL 相同的返回格式） ----
    @staticmethod
    def _fmt_val(v):
        """datetime → str（去掉自动附加的 +00:00 时区后缀）"""
        if isinstance(v, datetime):
            return v.strftime('%Y-%m-%d %H:%M:%S')
        return v

    @staticmethod
    def _one(queryset, single=True):
        """ORM 结果 → dict（兼容旧 raw SQL 返回格式）"""
        if single:
            obj = next(iter(queryset), None)
            if obj is None:
                return None
            if hasattr(obj, '_meta'):
                d = {f.attname: InputAndQuery._fmt_val(getattr(obj, f.attname)) for f in obj._meta.fields}
                d['id'] = obj.id
                return d
            else:
                return {k: InputAndQuery._fmt_val(v) for k, v in dict(obj).items()}
        else:
            results = []
            for obj in queryset:
                if hasattr(obj, '_meta'):
                    d = {f.attname: InputAndQuery._fmt_val(getattr(obj, f.attname)) for f in obj._meta.fields}
                    d['id'] = obj.id
                    results.append(d)
                else:
                    results.append({k: InputAndQuery._fmt_val(v) for k, v in dict(obj).items()})
            return results

    @staticmethod
    def _build_q(filters):
        """将 text_filters dict 转为 Q() 对象（icontains = LIKE '%x%'）"""
        q = Q()
        if filters.get('company_name'):
            q &= Q(company_name__icontains=filters['company_name'])
        if filters.get('uname'):
            q &= Q(uname__icontains=filters['uname'])
        if filters.get('message'):
            q &= Q(message__icontains=filters['message'])
        return q

    # ================================================================
    # 查询（SELECT）— 已改为 Django ORM
    # ================================================================

    def query_message1(self, num, page, kw):
        """查询 q_getmessage（分页 + 动态条件，kw 为 qm_kw 返回的 tuple）"""
        text_filters, exact_kw = kw
        qs = (QGetMessage.objects
              .filter(status=0)
              .exclude(data_source=444))
        if text_filters:
            qs = qs.filter(self._build_q(text_filters))
        if exact_kw:
            for part in exact_kw.split(' and '):
                part = part.strip()
                if '=' in part:
                    k, v = part.split('=', 1)
                    k = k.strip().strip('`')
                    v = v.strip().strip().strip('"').strip("'")
                    if v:
                        field = {'q_env': 'q_env', 'version': 'version',
                                 'company_id': 'company_id',
                                 'data_source': 'data_source'}.get(k)
                        if field:
                            qs = qs.filter(**{field: v})

        qs = qs.annotate(
            _sort=Coalesce('update_time', 'create_time')
        ).order_by('-_sort', '-id')
        qs = qs[self._esc_int(page):self._esc_int(page) + self._esc_int(num)]
        return self._one(qs, single=False)

    def query_message_by_dsandnum(self, dss, num):
        """按 data_source 列表查询近 N 条，合并后按更新时间倒序"""
        dss = [self._esc_int(d) for d in dss] if isinstance(dss, list) else [self._esc_int(dss)]
        qs = (QGetMessage.objects
              .filter(data_source__in=dss, status=0)
              .annotate(_sort=Coalesce('update_time', 'create_time'))
              .order_by('-_sort'))
        if int(num) > 0:
            qs = qs[:int(num)]
        return self._one(qs, single=False)

    def query_message_ops(self, keyword="", env="", uname="", limit=50):
        """企业操作日志（q_getmessage 全项目流水）：keyword 模糊匹配企业名/操作人/操作内容(OR)，env 精确筛选，limit 条数"""
        qs = (QGetMessage.objects
              .filter(status=0)
              .exclude(data_source=444))
        if env:
            qs = qs.filter(q_env=env)
        if uname:
            qs = qs.filter(uname__icontains=uname)
        if keyword:
            qs = qs.filter(
                Q(company_name__icontains=keyword) |
                Q(uname__icontains=keyword) |
                Q(message__icontains=keyword)
            )
        qs = qs.annotate(
            _sort=Coalesce('update_time', 'create_time')
        ).order_by('-_sort', '-id')
        return self._one(qs[:self._esc_int(limit)], single=False)

    def qm_kw(self, env, vers, compid, compname, uname, minfo):
        """
        根据字段拼接查询条件（兼容旧接口，返回 text_filters + exact_kw）
        """
        envval = f'`q_env` = "{self._esc(env)}" and ' if env else ''
        versval = f'`version` = {self._esc_int(vers)} and ' if vers else ''
        cidval = f'`company_id` = {self._esc_int(compid)} and ' if compid else ''

        text_filters = {}
        if compname: text_filters['company_name'] = compname
        if uname: text_filters['uname'] = uname
        if minfo: text_filters['message'] = minfo

        exact_kw = envval + versval + cidval
        return text_filters, exact_kw

    def query_message_total(self, kw):
        """查询 q_getmessage 总数"""
        qs = (QGetMessage.objects
              .filter(status=0)
              .exclude(data_source=444))

        text_filters, exact_kw = kw
        if text_filters:
            qs = qs.filter(self._build_q(text_filters))
        if exact_kw:
            for part in exact_kw.split(' and '):
                part = part.strip()
                if '=' in part:
                    k, v = part.split('=', 1)
                    k = k.strip().strip('`')
                    v = v.strip().strip().strip('"').strip("'")
                    if v:
                        field = {'q_env': 'q_env', 'version': 'version',
                                 'company_id': 'company_id',
                                 'data_source': 'data_source'}.get(k)
                        if field:
                            qs = qs.filter(**{field: v})
        return {"c": qs.count()}

    def query_cnbycid(self, companyId, env):
        """按企业 ID + 环境查企业名（调用方用 len(cn)==0 判空，确保返回 dict 或 {}）"""
        d = self._one(
            QGetMessage.objects
            .filter(company_id=companyId, q_env=env)
            .order_by('-id')[:1],
            single=True,
        )
        return d if d is not None else {}

    def query_uid(self, user, version=(0, 99)):
        """按用户名 + 版本查用户 ID"""
        d = self._one(
            User.objects
            .filter(user=user, version__in=version, deleted=0)
            .values('id')[:1],
            single=True,
        )
        return d

    def query_userInfo_byuuid(self, uuid):
        """按 uuid 查用户完整信息"""
        d = self._one(
            User.objects.filter(uuid=self._esc_int(uuid)),
            single=True,
        )
        return d

    def query_roles_byuuid(self, uuid):
        """按 auth_user.id(uuid)查用户角色列表，返回 [{'code','legacy_mr'},...]"""
        role_ids = (UserRole.objects
                    .filter(user_uuid=self._esc_int(uuid))
                    .values_list('role_id', flat=True))
        if not role_ids:
            return []
        qs = Role.objects.filter(id__in=role_ids).values('code', 'legacy_mr')
        return list(qs)

    def query_mr_byuuid(self, uuid):
        """按 uuid 推导 session['mr']（旧 menu_role 语义）。无角色时回退普通用户=2"""
        roles = self.query_roles_byuuid(uuid)
        if not roles:
            return 2
        mrs = [r['legacy_mr'] for r in roles if r['legacy_mr'] is not None]
        return max(mrs) if mrs else 2

    def query_menu_keys_byuuid(self, uuid):
        """按 auth_user.id 查用户拥有的菜单 key 集合（去重）"""
        role_ids = list(
            UserRole.objects
            .filter(user_uuid=self._esc_int(uuid))
            .values_list('role_id', flat=True)
        )
        if not role_ids:
            return list(PUBLIC_MENUS)
        keys = list(
            RoleMenu.objects
            .filter(role_id__in=role_ids)
            .values_list('menu_key', flat=True)
        )
        return list(set(keys))

    def query_count(self, user):
        """查用户是否存在（按用户名）"""
        cnt = User.objects.filter(user=user, deleted=0).count()
        # 兼容旧格式：dict with 'c' and 'user'
        return {"c": cnt, "user": user}

    def query_user_byuserl1(self, user):
        """按用户名前缀模糊查最近一个"""
        d = self._one(
            User.objects
            .filter(user__startswith=user, deleted=0)
            .order_by('-id')[:1],
            single=True,
        )
        return d

    def query_count_byname(self, name):
        """按姓名查用户是否存在"""
        cnt = User.objects.filter(name=name, deleted=0).count()
        return {"c": cnt}

    def query_uuidbyname(self, ln):
        """按登录名查 id/uuid"""
        d = self._one(
            User.objects
            .filter(user=ln, deleted=0)
            .values('id', 'uuid')[:1],
            single=True,
        )
        print(f'pub_InputAndQquery--query_uuidbyname:{d}')
        return d

    def query_opraterName(self):
        """查所有操作人列表（GROUP BY uname）"""
        qs = (QGetMessage.objects
              .values('uname')
              .annotate(cnt=Count('id'))
              .order_by('uname'))
        return list(qs)

    def query_cidbyphone(self, phone, env="prod"):
        """按手机号模糊查企业"""
        d = self._one(
            QGetMessage.objects
            .filter(message__icontains=phone, version=3, q_env=env)
            .values('company_id', 'company_name')[:1],
            single=True,
        )
        return d

    def query_reqhis(self, uid):
        """查请求历史"""
        return self._one(
            RequestHistory.objects.filter(uid=self._esc_int(uid), status='0'),
            single=False,
        )

    def query_urlInReqhis(self, uid, host, url):
        """按 uid+host+url 精确查请求历史"""
        d = self._one(
            RequestHistory.objects.filter(
                uid=uid, host=host, url=url, status='0',
            )[:1],
            single=True,
        )
        return d

    def query_aiText(self, user_id=None, title=None, content=None):
        """查 AI 文本"""
        qs = AiText.objects.filter(deleted=0)
        if user_id: qs = qs.filter(user_id=user_id)
        if title: qs = qs.filter(title=title)
        if content: qs = qs.filter(content__icontains=content)
        return self._one(qs, single=False)

    def query_mprecord(self, num, page, qkey):
        """查小程序记录（模糊搜索 + 分页）"""
        q = (
            Q(phone__icontains=qkey) |
            Q(company_id__icontains=qkey) |
            Q(company_name__icontains=qkey) |
            Q(app_id__icontains=qkey)
        )
        qs = (MiniprogramRecord.objects
              .filter(q, deleted='0')
              .annotate(_sort=Coalesce('update_time', 'create_time'))
              .order_by('-_sort', '-id'))
        qs = qs[self._esc_int(page):self._esc_int(page) + self._esc_int(num)]
        return self._one(qs, single=False)

    def query_mprecord_totalpage(self, qkey):
        """查小程序记录总数（调用方用 [0]['c']，返回 list）"""
        q = (
            Q(phone__icontains=qkey) |
            Q(company_id__icontains=qkey) |
            Q(company_name__icontains=qkey) |
            Q(app_id__icontains=qkey)
        )
        cnt = (MiniprogramRecord.objects.filter(q, deleted='0').count())
        return [{"c": cnt}]

    # ================================================================
    # 更新 / 新增 — 已改为 Django ORM
    # ================================================================

    def _now(self):
        """当前时间 — timezone-aware"""
        return timezone.now()

    def delete_user(self, ln):
        """软删除用户（原 update_userInfo，modkw 恒为 'deleted = 1'）"""
        return User.objects.filter(user=ln, deleted=0).update(deleted=1)

    def set_user_role(self, uuid, legacy_mr):
        """按 legacy_mr 设置用户单一角色（先清后插）。返回 1 成功 / 0 无此角色"""
        role = Role.objects.filter(legacy_mr=self._esc_int(legacy_mr)).first()
        if role is None:
            return 0
        UserRole.objects.filter(user_uuid=self._esc_int(uuid)).delete()
        UserRole.objects.create(
            user_uuid=self._esc_int(uuid), role_id=role.id, created_at=self._now(),
        )
        return 1

    def update_reqhis(self, id, header, params):
        """更新请求历史的 header/param"""
        return RequestHistory.objects.filter(id=self._esc_int(id), status='0').update(
            header=header, param=params, update_time=self._now(),
        )

    def del_message(self, id):
        return QGetMessage.objects.filter(id=self._esc_int(id), status=0).update(status=1)

    def update_aiText_content(self, id, content):
        """更新 AI 文本的 content"""
        return AiText.objects.filter(id=self._esc_int(id), deleted=0).update(
            content=content, update_time=self._now(),
        )

    def del_aiText(self, id):
        """软删除 AI 文本记录"""
        return AiText.objects.filter(id=self._esc_int(id), deleted=0).update(deleted=1)

    def inst_aiText(self, uid, title, content):
        obj = AiText.objects.create(
            user_id=self._esc_int(uid), title=title, content=content,
            create_time=self._now(),
        )
        return obj.id

    # ---- Agent 会话（独立表 agent_chat，与 aitools 隔离）----
    def query_agent_chat(self, user_id=None, title=None):
        """查 Agent 会话列表"""
        qs = AgentChat.objects.filter(deleted=0)
        if user_id: qs = qs.filter(user_id=user_id)
        if title: qs = qs.filter(title=title)
        return self._one(qs, single=False)

    def inst_agent_chat(self, uid, title, content):
        obj = AgentChat.objects.create(
            user_id=self._esc_int(uid), title=title, content=content,
            create_time=self._now(),
        )
        return obj.id

    def update_agent_chat_content(self, id, content):
        return AgentChat.objects.filter(id=self._esc_int(id), deleted=0).update(
            content=content, update_time=self._now(),
        )

    def del_agent_chat(self, id):
        return AgentChat.objects.filter(id=self._esc_int(id), deleted=0).update(deleted=1)

    # ---- mmeett 操作日志（供 Agent 汇总）----
    def inst_mmeett_op_log(self, uid, uname, env, action, params, result, success):
        """记录一条 mmeett 操作日志"""
        obj = MmeettOpLog.objects.create(
            user_id=self._esc_int(uid), uname=uname, env=env, action=action,
            params=params, result=result, success=self._esc_int(success),
            create_time=self._now(),
        )
        return obj.id

    def query_mmeett_op_log(self, user_id=None, env=None, action=None,
                            start_time=None, end_time=None, limit=200):
        """查 mmeett 操作日志。user_id/env/action 可选；start_time/end_time 为 'YYYY-MM-DD HH:MM:SS' 字符串"""
        qs = MmeettOpLog.objects.all()
        if user_id is not None and str(user_id) != '':
            qs = qs.filter(user_id=self._esc_int(user_id))
        if env:
            qs = qs.filter(env=env)
        if action:
            qs = qs.filter(action=action)
        if start_time:
            qs = qs.filter(create_time__gte=self._parse_dt(start_time))
        if end_time:
            qs = qs.filter(create_time__lte=self._parse_dt(end_time))
        qs = qs[:self._esc_int(limit)]
        return self._one(qs, single=False)

    @staticmethod
    def _parse_dt(s):
        """字符串时间 -> aware datetime，避免 naive datetime 警告"""
        try:
            dt = datetime.fromisoformat(str(s).replace('Z', '+00:00'))
        except ValueError:
            return s  # 交给 Django 自行处理
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
        return dt

    def inst_usertest(self, uuid, ln, name, pwd, vs):
        obj = User.objects.create(
            uuid=self._esc_int(uuid), user=ln, name=name, passwd=pwd,
            version=self._esc_int(vs), create_time=self._now(),
        )
        return obj.id

    def inst_reqhis(self, uid, method, host, url, header, param):
        obj = RequestHistory.objects.create(
            uid=self._esc_int(uid), method=method, host=host, url=url,
            header=header, param=param, create_time=self._now(),
        )
        return obj.id

    def inst_data(self, uid, uname, q_env, company_id, company_name, message, data_source, server_side, sversion):
        obj = QGetMessage.objects.create(
            uid=self._esc_int(uid), uname=uname, q_env=q_env,
            company_id=str(company_id), company_name=company_name,
            message=message, data_source=self._esc_int(data_source),
            server_side=self._esc_int(server_side), version=self._esc_int(sversion),
            create_time=self._now(),
        )
        return obj.id

    def inst_mprecord(self, phone, cid, cn, appid, oc, uid, un):
        obj = MiniprogramRecord.objects.create(
            phone=phone, company_id=cid, company_name=cn, app_id=appid,
            oprate_content=oc, user_id=self._esc_int(uid), user_name=un,
            create_time=self._now(),
        )
        return obj.id

    def inst_domain_status(self, company_id, app_id, status):
        obj = MiniprogramCompanyDomainStatus.objects.create(
            company_id=company_id, app_id=app_id, status=str(status),
            create_time=self._now(),
        )
        return obj.id

    def query_domain_status(self, appid):
        return self._one(
            MiniprogramCompanyDomainStatus.objects
            .filter(app_id=appid, deleted='0')
            .order_by('-id')[:1],
            single=True,
        )

    def update_domain_status(self, status, id):
        return MiniprogramCompanyDomainStatus.objects.filter(
            id=self._esc_int(id), deleted='0',
        ).update(status=str(status), update_time=self._now())

    def inst_tester_status(self, company_id, wechat_id, status):
        obj = MiniprogramBindWechat.objects.create(
            company_id=company_id, wechat_id=wechat_id, status=str(status),
            create_time=self._now(),
        )
        return obj.id

    def query_tester_status(self, cid, wcid):
        return self._one(
            MiniprogramBindWechat.objects
            .filter(company_id=self._esc_int(cid), wechat_id=wcid, deleted='0')
            .order_by('-id')[:1],
            single=True,
        )

    def update_tester_status(self, status, id):
        return MiniprogramBindWechat.objects.filter(
            id=self._esc_int(id), deleted='0',
        ).update(status=str(status), update_time=self._now())
