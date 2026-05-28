# 🏠 Lewis' Houses — 房屋租赁管理系统

一个轻量级的 Web 应用程序，用于管理出租房源、租赁合同（扫描件/图片）和房屋照片，支持随时随地通过浏览器访问。

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0+-lightgrey) ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite) ![License](https://img.shields.io/badge/License-MIT-green)

---

## 功能一览

| 功能 | 说明 |
|------|------|
| **🏠 房源管理** | 添加、编辑、删除房源，记录地址、类型、状态和描述 |
| **📄 合同管理** | 上传合同 PDF/扫描件，记录租客信息、租金、押金、租期 |
| **📸 照片管理** | 上传室内/室外/外观照片，分类标签，点击放大浏览 |
| **📋 租赁历史** | 结束租约时自动归档，保留完整历史记录 |
| **📊 仪表盘** | 房源总览卡片 + 统计数据（已租/空置/维修中） |
| **📱 响应式设计** | 桌面、平板、手机均可流畅使用 |
| **🔒 安全登录** | 密码保护，基于会话的身份认证 |

---

## 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/tsuimanlung/RentalContract.git
cd RentalContract

# 2. 创建虚拟环境（推荐）
python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行应用
python app.py
```

打开浏览器访问 **http://127.0.0.1:5000**

### 默认登录账号

| 字段 | 值 |
|------|-----|
| 用户名 | `admin` |
| 密码 | `admin123` |

> ⚠️ **首次登录后请立即修改默认密码！**

---

## 项目结构

```
RentalContract/
├── app.py                  # Flask 主应用（路由、认证、文件处理）
├── models.py               # 数据库模型（SQLAlchemy ORM）
├── forms.py                # WTForms 表单定义
├── config.py               # 应用配置
├── requirements.txt        # Python 依赖
├── .gitignore
├── README.md
├── templates/              # Jinja2 HTML 模板
│   ├── base.html           # 基础布局（导航栏）
│   ├── login.html          # 登录页面
│   ├── dashboard.html      # 控制台/房源总览
│   ├── property_form.html  # 添加/编辑房源表单
│   └── property_detail.html # 房源详情（含标签页）
├── static/
│   ├── css/style.css       # 自定义样式
│   └── js/main.js          # 前端交互
└── uploads/
    ├── contracts/           # 合同文件存储
    └── photos/              # 照片文件存储
```

---

## 数据模型

| 模型 | 说明 |
|------|------|
| **User** | 系统用户（登录认证） |
| **Property** | 房源（名称、地址、类型、状态、描述） |
| **Contract** | 合同（租客、租期、租金、押金、附件） |
| **Photo** | 照片（类型、文件路径、描述） |
| **RentalHistory** | 租赁历史（归档的历史租约） |

---

## 部署指南

### 方式一：Linux 服务器（推荐）

```bash
# 安装生产级 WSGI 服务器
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

建议配合 `systemd` 或 `supervisor` 保持进程持续运行，并使用 Nginx 反向代理配置 SSL 证书。

### 方式二：Windows 服务器

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 "app:create_app()"
```

### 方式三：云平台部署

以下平台提供免费套餐，适合个人使用：
- [PythonAnywhere](https://www.pythonanywhere.com/)
- [Render](https://render.com/)
- [Railway](https://railway.app/)

---

## 安全建议

1. 修改 `config.py` 中的 `SECRET_KEY`（生产环境务必更换）
2. 首次登录后立即修改默认管理员密码
3. 生产环境启用 HTTPS（推荐 Nginx + Let's Encrypt）
4. 考虑将默认 SQLite 替换为 PostgreSQL（高并发场景）

---

## 开发计划

- [ ] 支持多用户
- [ ] Docker 部署支持
- [ ] 数据导出/备份
- [ ] 按条件搜索/筛选房源
- [ ] 多语言切换

---

## 许可证

[MIT License](LICENSE) — 欢迎自由使用、修改和分享。

---

由 [tsuimanlung](https://github.com/tsuimanlung) 用心制作 ❤️
