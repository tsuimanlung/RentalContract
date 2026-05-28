#!/bin/bash
# ==============================================
# Lewis' Houses — Oracle Cloud Deployment Script
# Tested on: Ubuntu 22.04 / 24.04 LTS (ARM/AMD)
# ==============================================
set -e

echo "========================================"
echo "  Lewis' Houses — 一键部署脚本"
echo "========================================"

# ---------- 变量 ----------
APP_DIR="$HOME/RentalContract"
DOMAIN=""  # 留空则用 IP 访问，填写域名（如 rental.lewis.com）

# ---------- 系统更新 ----------
echo "[1/6] 更新系统包..."
sudo apt update && sudo apt upgrade -y

# ---------- 安装依赖 ----------
echo "[2/6] 安装 Python、Nginx..."
sudo apt install -y python3 python3-pip python3-venv nginx git

# ---------- 克隆项目 ----------
echo "[3/6] 克隆项目..."
if [ -d "$APP_DIR" ]; then
    echo "  项目已存在，尝试更新..."
    cd "$APP_DIR" && git pull
else
    git clone https://github.com/tsuimanlung/RentalContract.git "$APP_DIR"
    cd "$APP_DIR"
fi

# ---------- 虚拟环境 ----------
echo "[4/6] 配置 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# ---------- 配置 systemd 服务 ----------
echo "[5/6] 配置开机自启服务..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 替换密钥
sed -i "s|SECRET_KEY = os.environ.get('SECRET_KEY') or 'lewis-houses-secret-key-change-in-production'|SECRET_KEY = os.environ.get('SECRET_KEY') or '$SECRET_KEY'|" config.py

sudo cp deploy/rental-contract.service /etc/systemd/system/
sudo sed -i "s|change-this-to-a-random-secret-key|$SECRET_KEY|" /etc/systemd/system/rental-contract.service
sudo systemctl daemon-reload
sudo systemctl enable rental-contract
sudo systemctl start rental-contract

echo "  服务状态:"
sudo systemctl status rental-contract --no-pager | head -5

# ---------- 配置 Nginx ----------
echo "[6/6] 配置 Nginx 反向代理..."
sudo cp deploy/nginx.conf /etc/nginx/sites-available/rental-contract

if [ -n "$DOMAIN" ]; then
    sudo sed -i "s|your-domain.com;|$DOMAIN;|" /etc/nginx/sites-available/rental-contract
fi

sudo ln -sf /etc/nginx/sites-available/rental-contract /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# ---------- 防火墙 ----------
echo "  配置防火墙..."
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable 2>/dev/null || true

# ---------- 完成 ----------
echo "========================================"
echo "  ✅ 部署完成！"
echo ""
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "获取IP失败")
echo "  访问地址: http://$SERVER_IP"
echo "  默认登录: admin / admin123"
echo ""
echo "  ⚠️  请立即修改默认密码！"
echo "========================================"
