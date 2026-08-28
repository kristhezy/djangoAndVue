"""
数据库性能保障模块
- 项目启动时自动检查并创建缺失的索引和 FTS5 表
- 对已有的索引/表不做重复操作（幂等）
"""
import logging
from django.db import connection, transaction  # type: ignore

logger = logging.getLogger('django')


def _has_index(table, index_name):
    """检查 SQLite 中某表是否已有指定索引"""
    with connection.cursor() as cur:
        cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name=%s AND name=%s",
                    [table, index_name])
        return cur.fetchone() is not None


def create_indexes():
    """为所有高频查询的表创建索引（幂等）"""
    idx_definitions = [
        # === q_getmessage（操作日志表，查询最频繁）===
        # 复合索引: status + data_source（每查询必有）
        ("q_getmessage", "idx_qmsg_status_ds", "(`status`, `data_source`)"),
        # 单列索引: 高频过滤字段
        ("q_getmessage", "idx_qmsg_company_id", "(`company_id`)"),
        ("q_getmessage", "idx_qmsg_q_env", "(`q_env`)"),
        ("q_getmessage", "idx_qmsg_version", "(`version`)"),
        # 排序字段索引（ORDER BY create_time / update_time DESC）
        ("q_getmessage", "idx_qmsg_create_time", "(`create_time` DESC)"),
        ("q_getmessage", "idx_qmsg_update_time", "(`update_time` DESC)"),
        # uname: GROUP BY + LIKE 查询（query_opraterName / qm_kw）
        ("q_getmessage", "idx_qmsg_uname", "(`uname`)"),
        # company_id + q_env: 精确查询组合（query_cnbycid）
        ("q_getmessage", "idx_qmsg_cid_env", "(`company_id`, `q_env`)"),
        # users 表
        ("users", "idx_users_user_deleted_ver", "(`user`, `deleted`, `version`)"),
        ("users", "idx_users_uuid", "(`uuid`)"),
        ("users", "idx_users_deleted", "(`deleted`)"),
        # request_history
        ("request_history", "idx_reqhis_uid_status", "(`uid`, `status`)"),
        # miniprogram_record
        ("miniprogram_record", "idx_mp_deleted", "(`deleted`)"),
        ("miniprogram_record", "idx_mp_phone", "(`phone`)"),
        ("miniprogram_record", "idx_mp_company_id", "(`company_id`)"),
        ("miniprogram_record", "idx_mp_company_name", "(`company_name`)"),
        ("miniprogram_record", "idx_mp_app_id", "(`app_id`)"),
        # miniprogram_company_domain_status
        ("miniprogram_company_domain_status", "idx_ds_appid_deleted", "(`app_id`, `deleted`)"),
        # miniprogram_bind_wechat
        ("miniprogram_bind_wechat", "idx_bw_cid_wcid_deleted", "(`company_id`, `wechat_id`, `deleted`)"),
        # ai_text
        ("ai_text", "idx_ai_deleted", "(`deleted`)"),
    ]

    created = 0
    for table, idx_name, columns in idx_definitions:
        try:
            if not _has_index(table, idx_name):
                sql = f'CREATE INDEX IF NOT EXISTS "{idx_name}" ON "{table}" {columns}'
                with connection.cursor() as cur:
                    cur.execute(sql)
                created += 1
                logger.info(f"ensure_db: 创建索引 {idx_name} ON {table}")
        except Exception as e:
            logger.warning(f"ensure_db: 创建索引 {idx_name} 失败: {e}")

    if created > 0:
        logger.info(f"ensure_db: 完成，新建 {created} 个索引")
    return created


def create_fts5_tables():
    """创建 FTS5 全文搜索虚拟表（幂等）"""
    fts_definitions = [
        # q_getmessage: 对 company_name / uname / message 建全文索引
        (
            "q_getmessage",
            "q_getmessage_fts",
            "company_name, uname, message",
        ),
        # miniprogram_record: 对 phone / company_id / company_name / app_id 建全文索引
        (
            "miniprogram_record",
            "miniprogram_record_fts",
            "phone, company_id, company_name, app_id",
        ),
    ]
    created = 0
    for content_table, fts_table, columns in fts_definitions:
        try:
            # 检查是否已存在
            with connection.cursor() as cur:
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=%s", [fts_table])
                if cur.fetchone() is None:
                    sql = (
                        f"CREATE VIRTUAL TABLE IF NOT EXISTS {fts_table} "
                        f"USING fts5({columns}, content='{content_table}', content_rowid='id')"
                    )
                    cur.execute(sql)
                    created += 1
                    logger.info(f"ensure_db: 创建 FTS5 表 {fts_table}")
        except Exception as e:
            logger.warning(f"ensure_db: 创建 FTS5 表 {fts_table} 失败: {e}")

    if created > 0:
        logger.info(f"ensure_db: 完成，新建 {created} 个 FTS5 表")
    return created


def rebuild_fts(table_name):
    """重建 FTS5 索引（数据变更后调用）"""
    fts_map = {
        "q_getmessage": "q_getmessage_fts",
        "miniprogram_record": "miniprogram_record_fts",
    }
    fts = fts_map.get(table_name)
    if not fts:
        return
    try:
        with connection.cursor() as cur:
            # 检查 FTS 表是否存在
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=%s", [fts])
            if cur.fetchone():
                cur.execute(f"INSERT INTO {fts}({fts}) VALUES('rebuild')")
                logger.info(f"ensure_db: 重建 FTS 索引 {fts}")
    except Exception as e:
        logger.warning(f"ensure_db: 重建 FTS 索引 {fts} 失败: {e}")


def ensure_lottery_table():
    """创建 lottery_records 表（替代 fmhis.json）— 幂等"""
    with connection.cursor() as cur:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lottery_records'")
        if cur.fetchone() is None:
            cur.execute("""
                CREATE TABLE lottery_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ltype TEXT NOT NULL,
                    numbers TEXT NOT NULL,
                    create_time DATETIME NOT NULL
                )
            """)
            cur.execute("CREATE INDEX idx_lottery_ltype ON lottery_records(ltype)")
            cur.execute("CREATE INDEX idx_lottery_create_time ON lottery_records(create_time)")
            logger.info("ensure_db: 创建 lottery_records 表")


def ensure_all():
    """启动时调用：确保所有性能优化就绪"""
    try:
        ensure_lottery_table()
        create_indexes()
        create_fts5_tables()
    except Exception as e:
        logger.warning(f"ensure_db: 初始化遇到问题（不影响功能）: {e}")
