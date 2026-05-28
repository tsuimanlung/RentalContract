
# 🏠 Lewis' Houses — Rental Property Management System

A lightweight web application for managing rental properties, contracts (scans/images), and property photos. Accessible from anywhere via any browser.

房屋租赁管理系统，用于管理房源信息、租赁合同（扫描件/图片）和房屋照片，支持随时随地通过浏览器访问。

## Features / 功能

- **Property Management / 房源管理** — Add, edit, delete properties with address, type, status, and description
- **Contract Management / 合同管理** — Upload contract PDFs/images per property, record tenant info, rent, deposit, lease period
- **Photo Gallery / 照片管理** — Upload indoor/outdoor/facade photos with categorized tags
- **Rental History / 租赁历史** — Auto-archive contracts when tenancy ends, maintain full history
- **Status Tracking / 状态追踪** — Visual badges for Rented / Vacant / Under Maintenance
- **Dashboard Overview / 仪表盘** — At-a-glance stats and property cards
- **Responsive Design / 响应式设计** — Works on desktop, tablet, and mobile
- **Secure / 安全** — Password-protected with session-based authentication

## Tech Stack / 技术栈

| Layer | Technology |
|-------|-----------|
| Backend | Python 3 + Flask |
| Database | SQLite (via SQLAlchemy ORM) |
| Frontend | Bootstrap 5, Font Awesome, vanilla JS |
| Auth | Flask-Login (session-based) |
| File Storage | Local filesystem (`uploads/`) |

## Quick Start / 快速开始

### Prerequisites / 前置要求

- Python 3.8+
- pip

### Installation / 安装

```bash
# 1. Clone the repository
git clone https://github.com/tsuimanlung/RentalContract.git
cd RentalContract

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

Open your browser and visit **http://127.0.0.1:5000**

### Default Login / 默认登录

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |

**Change the default password immediately after first login!**
首次登录后请立即修改默认密码！

## Project Structure / 项目结构

```
RentalContract/
├── app.py                 # Main Flask application (routes, auth, file handling)
├── models.py              # SQLAlchemy database models
├── forms.py               # WTForms form definitions
├── config.py              # Application configuration
├── requirements.txt       # Python dependencies
├── .gitignore
├── README.md
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base layout with navbar
│   ├── login.html         # Login page
│   ├── dashboard.html     # Property overview / stats
│   ├── property_form.html # Add / Edit property form
│   └── property_detail.html # Detail page with tabs
├── static/
│   ├── css/style.css      # Custom styles
│   └── js/main.js         # Front-end interactivity
└── uploads/
    ├── contracts/         # Contract files (PDF, images)
    └── photos/            # Property photos
```

## Database Schema / 数据模型

- **User** — system login
- **Property** — name, address, type, status, description
- **Contract** — tenant info, lease period, rent, deposit, file attachment
- **Photo** — type (indoor/outdoor/facade), file path, description
- **RentalHistory** — archived tenancy records

## Deployment / 部署

### Option 1: Linux Server (Recommended)

```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

Use `systemd` or `supervisor` to keep the process running. Set up Nginx as a reverse proxy for SSL and static file serving.

### Option 2: Docker (coming soon)

### Option 3: PythonAnywhere / Render

These platforms offer free tiers suitable for small-scale personal use.

## Security Notes / 安全提示

- Change the default `SECRET_KEY` in `config.py` before production use
- Change the default admin password immediately
- Use HTTPS in production (recommend Nginx + Let's Encrypt)
- The app uses SQLite by default — consider PostgreSQL for production

## License / 许可

MIT License — feel free to use, modify, and share.

---

Built with ❤️ by [tsuimanlung](https://github.com/tsuimanlung)
