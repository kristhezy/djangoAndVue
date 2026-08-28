-- mmeett 操作日志表 mmeett_op_log
-- 用途：记录 mmeettOpen 页面的各类操作（注册/充值/降级/购买/算力/安置/资产变更/删号等），供 Agent 汇总
-- 数据库：SQLite（db.sqlite3），由 mysqlite.models.MmeettOpLog 以 managed=False 方式映射
-- 幂等：可重复执行，表已存在时跳过
-- 用法：sqlite3 db.sqlite3 < scripts/create_mmeett_op_log.sql

CREATE TABLE IF NOT EXISTS mmeett_op_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,                          -- 登录用户ID（对应 session uid）
    uname       TEXT,                             -- 登录用户名
    env         TEXT,                             -- 环境 test/prod/ydtest
    action      TEXT,                             -- 操作类型（mmeettRegist/buyVip/sendComputing 等）
    params      TEXT,                             -- 关键参数摘要(JSON)
    result      TEXT,                             -- 结果摘要
    success     INTEGER DEFAULT 0,                -- 1成功 0失败
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
