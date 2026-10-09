#!/bin/bash
cd "$(dirname "$0")"

# 确保 Redis 已就绪，避免重启后空窗期报 Connection refused
if ! redis-cli ping >/dev/null 2>&1; then
    echo "Redis 未运行，正在启动..."
    brew services start redis >/dev/null 2>&1
    # 最多等待 15 秒
    for _ in $(seq 1 15); do
        redis-cli ping >/dev/null 2>&1 && break
        sleep 1
    done
    if ! redis-cli ping >/dev/null 2>&1; then
        echo "错误：Redis 启动失败，请手动执行 brew services start redis 后重试"
        exit 1
    fi
    echo "Redis 已就绪"
fi

# 确保日志目录存在，并把所有 print 的 stdout/stderr 用 tee 同时输出到终端和文件（兜底落盘）
mkdir -p logs

# console.log 大小轮转：超过 50MB 清空（shell 重定向无自带轮转，避免无限增长）
if [ -f logs/console.log ] && [ "$(stat -f%z logs/console.log 2>/dev/null || echo 0)" -gt 52428800 ]; then
    echo "console.log 超过 50MB，已清空" >> logs/console.log.rotated 2>/dev/null
    : > logs/console.log
fi

# --reload-dir 限定只监视后端代码目录（已安装 watchfiles，事件驱动、不再全盘轮询扫描）
/Users/imc/vllm/yes/envs/py310/bin/python3 -m uvicorn djangoPlant.asgi:application --host 0.0.0.0 --port 8001 --reload --reload-dir djangoPlant 2>&1 | tee -a logs/console.log
