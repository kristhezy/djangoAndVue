import pymysql  # type: ignore
from dbutils.pooled_db import PooledDB  # type: ignore
import os

# 数据库密码从环境变量读取：
#   环境变量 DB_PASSWORD          覆盖所有库密码（优先级最高）
#   环境变量 DB_PASSWORD_XCARD / DB_PASSWORD_MMEETT  按库名覆盖
#   未设置时使用默认值（仅限开发环境）
_DB_DEFAULT_PASSWORDS = {
    "192.168.1.77":   os.environ.get("DB_PASSWORD_XCARD", "Xingrui@DCDB123"),
    "111.119.213.78": os.environ.get("DB_PASSWORD_MMEETT", ""),
}

def _get_db_password(host_default):
    """全局 DB_PASSWORD 或按 host 匹配的默认密码"""
    pwd = os.environ.get("DB_PASSWORD")
    if pwd is not None:
        return pwd
    return _DB_DEFAULT_PASSWORDS.get(host_default, "")


class mySqlPool(object):
    # 连接池缓存: key=(host,user,password,dbname) -> PooledDB实例
    _pool_cache = {}

    def __init__(self, ms, dbname):
        if ms == "xcard":
            host = os.environ.get("DB_HOST_XCARD", "192.168.1.77")
            user = os.environ.get("DB_USER_XCARD", "root")
            password = _get_db_password(host)
        elif ms == "mmeett":
            host = os.environ.get("DB_HOST_MMEETT", "111.119.213.78")
            user = os.environ.get("DB_USER_MMEETT", "wecard")
            password = _get_db_password(host)
        else:
            host = 'localhost'
            user = 'root'
            password = ''
        cache_key = (host, user, password, dbname)
        if cache_key in self._pool_cache:
            self.pool = self._pool_cache[cache_key]
        else:
            self.pool = PooledDB(
                creator=pymysql,
                host=host,
                port=3306,
                user=user,
                password=password,
                database=dbname,
                charset='utf8mb4',
                autocommit=True,
                maxconnections=20,
                mincached=5,
                maxcached=10,
                maxusage=1000
            )
            self._pool_cache[cache_key] = self.pool

    def execute(self, sql, params):
        """执行增删改，返回受影响行数"""
        with self.pool.connection() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                rowcount = cur.execute(sql, params)
                print(f"execute result: mysql = {sql}, {params}; rowcount = {rowcount}")
                return rowcount
