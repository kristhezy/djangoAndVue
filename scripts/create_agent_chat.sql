-- Agent 会话表 agent_chat
-- 用途：Agent 助手的历史会话持久化（与 aitools 的 ai_text 表隔离）
-- 数据库：SQLite（db.sqlite3），由 mysqlite.models.AgentChat 以 managed=False 方式映射
-- 幂等：可重复执行，表已存在时跳过
-- 用法：sqlite3 db.sqlite3 < scripts/create_agent_chat.sql

CREATE TABLE IF NOT EXISTS agent_chat (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,                          -- 用户ID（对应 users.id / session uid）
    title       TEXT,                             -- 会话标题（取首条提问）
    content     TEXT,                             -- 多轮对话 JSON: [{"ask":"...","answer":"..."}, ...]
    deleted     INTEGER DEFAULT 0,                -- 软删除标记 0=正常 1=已删除
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP
);
