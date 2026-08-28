"""Django Models for existing SQLite tables (managed=False, 不创建/修改表结构)"""
from django.db import models  # type: ignore


class QGetMessage(models.Model):
    """操作日志表 q_getmessage"""
    uid = models.IntegerField(null=True, blank=True)
    uname = models.CharField(max_length=255, null=True, blank=True)
    q_env = models.CharField(max_length=255, null=True, blank=True)
    company_id = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    status = models.IntegerField(default=0)
    data_source = models.IntegerField(null=True, blank=True)
    server_side = models.IntegerField(null=True, blank=True)
    version = models.IntegerField(null=True, blank=True)
    create_time = models.DateTimeField(null=True, blank=True)
    update_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'q_getmessage'
        ordering = ['-id']

    def __str__(self):
        return f"QGetMessage({self.id}, {self.company_name}, {self.uname})"


class User(models.Model):
    """测试平台用户表 users"""
    uuid = models.IntegerField(null=True, blank=True)
    user = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    passwd = models.CharField(max_length=255, null=True, blank=True)
    version = models.IntegerField(null=True, blank=True)
    create_time = models.DateTimeField(null=True, blank=True)
    update_time = models.DateTimeField(null=True, blank=True)
    deleted = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'users'
        ordering = ['-id']

    def __str__(self):
        return f"User({self.id}, {self.user})"


class Role(models.Model):
    """角色表 role（权限改造新增，managed=False）"""
    code = models.CharField(max_length=32, unique=True, null=True, blank=True)
    name = models.CharField(max_length=64, null=True, blank=True)
    legacy_mr = models.IntegerField(null=True, blank=True)  # 兼容旧 menu_role 值：99=admin 2=user
    sort = models.IntegerField(default=0)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'role'
        ordering = ['sort', 'id']

    def __str__(self):
        return f"Role({self.id}, {self.code})"


class UserRole(models.Model):
    """用户-角色关联表 user_role（user_uuid = auth_user.id）"""
    user_uuid = models.IntegerField(null=True, blank=True)
    role_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'user_role'
        ordering = ['id']

    def __str__(self):
        return f"UserRole({self.user_uuid}, role={self.role_id})"


class RoleMenu(models.Model):
    """角色-菜单关联表 role_menu（角色拥有哪些菜单 key）"""
    role_id = models.IntegerField(null=True, blank=True)
    menu_key = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'role_menu'
        ordering = ['id']

    def __str__(self):
        return f"RoleMenu({self.role_id}, {self.menu_key})"


class RequestHistory(models.Model):
    """请求历史表 request_history"""
    uid = models.IntegerField(null=True, blank=True)
    method = models.CharField(max_length=255, null=True, blank=True)
    host = models.CharField(max_length=255, null=True, blank=True)
    url = models.TextField(null=True, blank=True)
    header = models.TextField(null=True, blank=True)
    param = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=255, default='0')  # TEXT
    create_time = models.DateTimeField(null=True, blank=True)
    update_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'request_history'
        ordering = ['-id']

    def __str__(self):
        return f"RequestHistory({self.id}, {self.host}{self.url})"


class AiText(models.Model):
    """AI 文本表 ai_text"""
    user_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    deleted = models.IntegerField(default=0)
    create_time = models.DateTimeField(null=True, blank=True)
    update_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'ai_text'
        ordering = ['-id']

    def __str__(self):
        return f"AiText({self.id}, {self.title})"


class AgentChat(models.Model):
    """Agent 会话表 agent_chat（与 aitools 的 ai_text 隔离）"""
    user_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    deleted = models.IntegerField(default=0)
    create_time = models.DateTimeField(null=True, blank=True)
    update_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'agent_chat'
        ordering = ['-id']

    def __str__(self):
        return f"AgentChat({self.id}, {self.title})"


class MmeettOpLog(models.Model):
    """mmeett 操作日志表 mmeett_op_log（记录 mmeettOpen 页面的各类操作，供 Agent 汇总）"""
    user_id = models.IntegerField(null=True, blank=True)          # 登录用户ID
    uname = models.CharField(max_length=255, null=True, blank=True)  # 登录用户名
    env = models.CharField(max_length=20, null=True, blank=True)  # test/prod/ydtest
    action = models.CharField(max_length=64, null=True, blank=True)  # 操作类型
    params = models.TextField(null=True, blank=True)              # 关键参数摘要(JSON)
    result = models.TextField(null=True, blank=True)              # 结果摘要
    success = models.IntegerField(default=0)                      # 1成功 0失败
    create_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'mmeett_op_log'
        ordering = ['-id']

    def __str__(self):
        return f"MmeettOpLog({self.id}, {self.action}, {self.env})"


class MiniprogramRecord(models.Model):
    """小程序记录表 miniprogram_record"""
    phone = models.CharField(max_length=255, null=True, blank=True)
    company_id = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    app_id = models.CharField(max_length=255, null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    user_name = models.CharField(max_length=255, null=True, blank=True)
    oprate_content = models.TextField(null=True, blank=True)
    deleted = models.CharField(max_length=255, default='0')
    create_time = models.DateTimeField(null=True, blank=True)
    update_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'miniprogram_record'
        ordering = ['-id']

    def __str__(self):
        return f"MiniprogramRecord({self.id}, {self.company_name})"


class MiniprogramCompanyDomainStatus(models.Model):
    """小程序域名状态表 miniprogram_company_domain_status"""
    company_id = models.CharField(max_length=255, null=True, blank=True)
    app_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, default='0')
    deleted = models.CharField(max_length=255, default='0')
    create_time = models.DateTimeField(null=True, blank=True)
    update_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'miniprogram_company_domain_status'
        ordering = ['-id']

    def __str__(self):
        return f"DomainStatus({self.id}, {self.company_id})"


class MiniprogramBindWechat(models.Model):
    """小程序绑定微信表 miniprogram_bind_wechat"""
    company_id = models.CharField(max_length=255, null=True, blank=True)
    wechat_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, default='0')
    deleted = models.CharField(max_length=255, default='0')
    create_time = models.DateTimeField(null=True, blank=True)
    update_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'miniprogram_bind_wechat'
        ordering = ['-id']

    def __str__(self):
        return f"BindWechat({self.id}, {self.company_id})"


class LotteryRecord(models.Model):
    """抽奖记录表 lottery_records — 替代 fmhis.json"""
    ltype = models.CharField(max_length=10, db_column='ltype')      # 'ssq' / 'dlt' / 'kl8'
    numbers = models.CharField(max_length=50)                       # '07,12,13,21,25,33 — 07'
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'lottery_records'
        ordering = ['-id']
