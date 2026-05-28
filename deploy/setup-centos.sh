#!/bin/bash
# ==============================================
# Lewis' Houses — CentOS / Oracle Linux 部署脚本
# 端口模式：直接通过 http://IP:5000 访问
# Tested on: CentOS 7, Oracle Linux 7/8
# ==============================================
set -e

echo "========================================"
echo "  Lewis' Houses — CentOS 一键部署脚本"
echo "  端口模式 (5000)"
echo "========================================"

APP_DIR="/opt/RentalContract"
PORT=5000

# ---------- 系统更新 ----------
echo "[1/5] 安装系统依赖..."
yum install -y epel-release
yum install -y python3 python3-pip python3-devel git gcc

# ---------- 克隆项目 ----------
echo "[2/5] 克隆项目..."
if [ -d "$APP_DIR" ]; then
    echo "  项目已存在，更新中..."
    cd "$APP_DIR" && git pull
else
    git clone https://github.com/tsuimanlung/RentalContract.git "$APP_DIR"
    cd "$APP_DIR"
fi

# ---------- 虚拟环境 ----------
echo "[3/5] 配置 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# ---------- 配置 systemd 服务 ----------
echo "[4/5] 配置开机自启服务..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 替换密钥
sed -i "s|SECRET_KEY = os.environ.get('SECRET_KEY') or 'lewis-houses-secret-key-change-in-production'|SECRET_KEY = os.environ.get('SECRET_KEY') or '$SECRET_KEY'|" config.py

# 生成 CentOS 兼容的 service 文件
cat > /etc/systemd/system/rental-contract.service << 'SERVICEEOF'
[Unit]
Description=Lewis' Houses — Rental Property Management
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/RentalContract
Environment="PATH=/opt/RentalContract/venv/bin"
ExecStart=/opt/RentalContract/venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 "app:create_app()"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICEEOF

systemctl daemon-reload
systemctl enable rental-contract
systemctl start rental-contract

echo "  服务状态:"
systemctl status rental-contract --no-pager | head -5

# ---------- 防火墙 ----------
echo "[5/5] 开放端口 $PORT..."
if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --add-port=$PORT/tcp --permanent
    firewall-cmd --reload
elif command -v iptables &> /dev/null; then
    iptables -I INPUT -p tcp --dport $PORT -j ACCEPT
    iptables-save > /etc/sysconfig/iptables 2>/dev/null || true
fi

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
