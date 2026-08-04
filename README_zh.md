# Creative AI Platform

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/node-18%2B-green)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.x-4FC08D)](https://vuejs.org/)

一个自托管的一站式 AI 创作平台，将 AI 对话、图像生成、视频生成和无限画布整合到一个统一的工作空间中。

## 功能特性

- **AI 对话** -- 支持多模型、多供应商的对话式 AI。支持上下文对话、文件上传，由最先进的语言模型提供智能回复。
- **图像生成** -- 通过文本提示词生成精美的图像。支持多种 AI 图像生成后端，可调整风格、分辨率和创意度参数。
- **视频生成** -- 从文本描述中生成短视频和动画。借助 AI 驱动的视频合成技术，将你的创意变为现实。
- **无限画布** -- 一个无边界的可视化工作空间，用于组织和展示你的创作成果。在可缩放、可平移的画布上排列图像、视频和文本。
- **多供应商支持** -- 同时连接多个 AI API 供应商。无需改变工作流程即可随时切换供应商。
- **历史记录与收藏** -- 所有创作自动保存。通过强大的筛选和标签功能，浏览、搜索和组织你的创作历史。

## 截图展示

> 截图即将推出，敬请期待！

## 技术栈

| 层级 | 技术 | 说明 |
|-------|-----------|-------------|
| **后端框架** | FastAPI (Python 3.10+) | 高性能异步 REST API |
| **前端框架** | Vue 3 + TypeScript | 现代化响应式 UI 框架 |
| **构建工具** | Vite | 快速前端构建与热更新 |
| **数据库** | SQLite / PostgreSQL | 基于 SQLAlchemy 的异步 ORM |
| **ORM** | SQLAlchemy 2.0 (异步) | 现代化异步数据库工具包 |
| **身份认证** | JWT (JSON Web Tokens) | 无状态认证，支持刷新令牌 |
| **AI 集成** | Agnes AI API | 统一的 AI 供应商网关 |
| **状态管理** | Pinia | 直观的 Vue 状态管理 |
| **CSS 框架** | Tailwind CSS | 实用优先的 CSS 框架 |
| **画布引擎** | Fabric.js / Konva.js | HTML5 Canvas 渲染引擎 |

## 快速开始

### 环境要求

- **Python 3.10+** -- [下载地址](https://www.python.org/downloads/)
- **Node.js 18+** -- [下载地址](https://nodejs.org/)
- **npm**（随 Node.js 一起安装）

### 安装

```bash
# 克隆仓库
git clone https://github.com/your-org/creative-ai-platform.git
cd creative-ai-platform
```

### 启动平台

**Linux / macOS：**

```bash
chmod +x start.sh
./start.sh
```

**Windows：**

```cmd
start.bat
```

**跨平台（Python）：**

```bash
python start.py
```

启动脚本会自动完成以下操作：

1. 检查 Python 3.10+ 和 Node.js 18+ 是否已安装
2. 创建 Python 虚拟环境
3. 安装所有后端和前端依赖
4. 将 `.env.example` 复制为 `.env`（如不存在）
5. 初始化数据库
6. 启动后端 API 服务器
7. 启动前端开发服务器

### 访问地址

| 服务 | 地址 |
|---------|-----|
| 前端界面 | [http://localhost:5173](http://localhost:5173) |
| 后端 API | [http://localhost:8000](http://localhost:8000) |
| API 文档 (Swagger) | [http://localhost:8000/docs](http://localhost:8000/docs) |
| API 文档 (ReDoc) | [http://localhost:8000/redoc](http://localhost:8000/redoc) |

### 默认管理员账号

| 字段 | 值 |
|-------|-------|
| 用户名 | `admin` |
| 密码 | `admin123` |
| 邮箱 | `admin@example.com` |

> 首次登录后请立即修改默认密码。

## 项目结构

```
creative-ai-platform/
├── backend/                    # FastAPI 后端
│   ├── api/                    # API 路由处理
│   │   ├── auth.py             # 认证接口
│   │   ├── chat.py             # 对话接口
│   │   ├── images.py           # 图像生成接口
│   │   ├── videos.py           # 视频生成接口
│   │   └── canvas.py           # 画布接口
│   ├── models/                 # SQLAlchemy ORM 模型
│   ├── schemas/                # Pydantic 请求/响应模式
│   ├── services/               # 业务逻辑层
│   ├── core/                   # 核心工具（配置、安全等）
│   ├── main.py                 # 应用入口
│   ├── init_db.py              # 数据库初始化脚本
│   ├── requirements.txt        # Python 依赖
│   └── .env.example            # 后端环境变量模板
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── components/         # 可复用 Vue 组件
│   │   ├── views/              # 页面级组件
│   │   ├── stores/             # Pinia 状态存储
│   │   ├── api/                # API 客户端层
│   │   ├── router/             # Vue Router 配置
│   │   └── assets/             # 静态资源
│   ├── package.json            # Node.js 依赖
│   └── vite.config.ts          # Vite 配置
├── data/                       # SQLite 数据库（自动生成）
├── start.sh                    # Linux/macOS 启动脚本
├── start.bat                   # Windows 启动脚本
├── start.py                    # 跨平台 Python 启动脚本
├── .env.example                # 环境变量模板
├── .gitignore                  # Git 忽略规则
├── README.md                   # 英文文档
├── README_zh.md                # 本文档（中文文档）
└── LICENSE                     # Apache 2.0 许可证
```

## API 文档

后端运行后，可通过以下地址访问交互式 API 文档：

- **Swagger UI**：[http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**：[http://localhost:8000/redoc](http://localhost:8000/redoc)

## 环境变量

| 变量 | 说明 | 默认值 |
|----------|-------------|---------|
| `DATABASE_URL` | 数据库连接字符串 | `sqlite+aiosqlite:///./data/app.db` |
| `JWT_SECRET` | JWT 签名密钥 | （必填） |
| `JWT_ALGORITHM` | JWT 签名算法 | `HS256` |
| `JWT_EXPIRATION_HOURS` | JWT 令牌过期时间 | `168` |
| `ENCRYPTION_KEY` | 数据加密的 Fernet 密钥 | （必填） |
| `DEFAULT_ADMIN_USERNAME` | 默认管理员用户名 | `admin` |
| `DEFAULT_ADMIN_PASSWORD` | 默认管理员密码 | `admin123` |
| `DEFAULT_ADMIN_EMAIL` | 默认管理员邮箱 | `admin@example.com` |
| `HOST` | 服务器绑定地址 | `0.0.0.0` |
| `PORT` | 服务器端口 | `8000` |
| `AGNES_API_BASE_URL` | Agnes AI API 基础地址 | `https://apihub.agnes-ai.com/v1` |
| `AGNES_API_KEY` | Agnes AI API 密钥 | （必填） |

## 参与贡献

我们欢迎所有形式的贡献！参与步骤如下：

1. Fork 本仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 提交你的更改（`git commit -m 'Add some amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 提交 Pull Request

请确保你的代码遵循项目的编码规范，并包含适当的测试。

## 许可证

本项目基于 Apache License 2.0 许可证开源 -- 详见 [LICENSE](LICENSE) 文件。

---

**Creative AI Platform** -- 以人工智能赋能创意创作。