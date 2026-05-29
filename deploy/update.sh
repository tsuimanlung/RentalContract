#!/bin/bash
# Lewis' Houses — 一键更新脚本
set -e

cd /opt/RentalContract

echo "[1/3] 拉取最新代码..."
git pull

echo "[2/3] 重启服务..."
systemctl stop rental-contract
sleep 2

# 清理残留进程（来自之前手动运行的旧进程）
OLD_PIDS=$(lsof -t -i :5000 2>/dev/null || true)
if [ -n "$OLD_PIDS" ]; then
    echo "  清理残留进程: $OLD_PIDS"
    kill -9 $OLD_PIDS 2>/dev/null || true
    sleep 1
fi

systemctl start rental-contract

echo "[3/3] 服务状态:"
systemctl status rental-contract --no-pager | head -5
echo ""
echo "✅ 更新完成！"
