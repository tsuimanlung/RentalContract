#!/bin/bash
# ==============================================
# Lewis' Houses — Oracle Cloud Deployment Script
# 端口模式：直接通过 http://IP:5000 访问
# Tested on: Ubuntu 22.04 / 24.04 LTS (ARM/AMD)
# ==============================================
set -e

echo "========================================"
echo "  Lewis' Houses — 一键部署脚本"
echo "  端口模式 (5000)"
echo "========================================"

APP_DIR="$HOME/RentalContract"
PORT=5000

# ---------- 系统更新 ----------
echo "[1/5] 更新系统包..."
sudo apt update && sudo apt upgrade -y

# ---------- 安装依赖 ----------
echo "[2/5] 安装 Python..."
sudo apt install -y python3 python3-pip python3-venv git

# ---------- 克隆项目 ----------
echo "[3/5] 克隆项目..."
if [ -d "$APP_DIR" ]; then
    echo "  项目已存在，更新中..."
    cd "$APP_DIR" && git pull
else
    git clone https://github.com/tsuimanlung/RentalContract.git "$APP_DIR"
    cd "$APP_DIR"
fi

# ---------- 虚拟环境 ----------
echo "[4/5] 配置 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# ---------- 配置 systemd 服务 ----------
echo "[5/5] 配置开机自启服务..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 替换密钥
sed -i "s|SECRET_KEY = os.environ.get('SECRET_KEY') or 'lewis-houses-secret-key-change-in-production'|SECRET_KEY = os.environ.get('SECRET_KEY') or '$SECRET_KEY'|" config.py

# 替换端口
sudo sed -i "s|0.0.0.0:5000|0.0.0.0:$PORT|" deploy/rental-contract.service
sudo sed -i "s|change-this-to-a-random-secret-key|$SECRET_KEY|" deploy/rental-contract.service

sudo cp deploy/rental-contract.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rental-contract
sudo systemctl start rental-contract

echo "  服务状态:"
sudo systemctl status rental-contract --no-pager | head -5

# ---------- 防火墙 ----------
echo "  开放端口 $PORT..."
sudo ufw allow $PORT/tcp
sudo ufw --force enable 2>/dev/null || true

# ---------- 完成 ----------
echo "========================================"
echo "  ✅ 部署完成！"
echo ""
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "获取IP失败")
echo "  访问地址: http://$SERVER_IP:$PORT"
echo "  默认登录: admin / admin123"
echo ""
echo "  ⚠️  请立即修改默认密码！"
echo "========================================"
