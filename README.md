# Creative AI Platform

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/node-18%2B-green)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.x-4FC08D)](https://vuejs.org/)

A self-hosted, all-in-one AI creation platform that brings together AI chat, image generation, video generation, and an infinite canvas into a single, unified workspace.

## Features

- **AI Chat** -- Conversational AI with support for multiple models and providers. Chat with context, upload files, and get intelligent responses powered by state-of-the-art language models.
- **Image Generation** -- Create stunning images from text prompts. Supports multiple AI image generation backends with adjustable parameters for style, resolution, and creativity.
- **Video Generation** -- Generate short-form videos and animations from text descriptions. Bring your ideas to life with AI-powered video synthesis.
- **Infinite Canvas** -- A boundless visual workspace for organizing your creative outputs. Arrange images, videos, and text on a zoomable, pannable canvas.
- **Multi-Provider Support** -- Connect to multiple AI API providers simultaneously. Switch between providers on the fly without changing your workflow.
- **History & Collections** -- All your creations are automatically saved. Browse, search, and organize your generation history with powerful filtering and tagging.

## Screenshots

> Screenshots coming soon. Stay tuned!

## Tech Stack

| Layer | Technology | Description |
|-------|-----------|-------------|
| **Backend Framework** | FastAPI (Python 3.10+) | High-performance async REST API |
| **Frontend Framework** | Vue 3 + TypeScript | Modern reactive UI framework |
| **Build Tool** | Vite | Fast frontend build and HMR |
| **Database** | SQLite / PostgreSQL | Async ORM with SQLAlchemy |
| **ORM** | SQLAlchemy 2.0 (async) | Modern async database toolkit |
| **Authentication** | JWT (JSON Web Tokens) | Stateless auth with refresh tokens |
| **AI Integration** | Agnes AI API | Unified AI provider gateway |
| **State Management** | Pinia | Intuitive Vue state management |
| **CSS Framework** | Tailwind CSS | Utility-first CSS framework |
| **Canvas** | Fabric.js / Konva.js | HTML5 Canvas rendering engine |

## Quick Start

### Prerequisites

- **Python 3.10+** -- [Download](https://www.python.org/downloads/)
- **Node.js 18+** -- [Download](https://nodejs.org/)
- **npm** (comes with Node.js)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/creative-ai-platform.git
cd creative-ai-platform
```

### Start the Platform

**Linux / macOS:**

```bash
chmod +x start.sh
./start.sh
```

**Windows:**

```cmd
start.bat
```

**Cross-platform (Python):**

```bash
python start.py
```

The start script will:

1. Check Python 3.10+ and Node.js 18+ are installed
2. Create a Python virtual environment
3. Install all backend and frontend dependencies
4. Copy `.env.example` to `.env` (if not exists)
5. Initialize the database
6. Start the backend API server
7. Start the frontend development server

### Access

| Service | URL |
|---------|-----|
| Frontend | [http://localhost:5173](http://localhost:5173) |
| Backend API | [http://localhost:8000](http://localhost:8000) |
| API Documentation (Swagger) | [http://localhost:8000/docs](http://localhost:8000/docs) |
| API Documentation (ReDoc) | [http://localhost:8000/redoc](http://localhost:8000/redoc) |

### Default Admin Account

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |
| Email | `admin@example.com` |

> Change the default password immediately after your first login.

## Project Structure

```
creative-ai-platform/
├── backend/                    # FastAPI backend
│   ├── api/                    # API route handlers
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── chat.py             # Chat endpoints
│   │   ├── images.py           # Image generation endpoints
│   │   ├── videos.py           # Video generation endpoints
│   │   └── canvas.py           # Canvas endpoints
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic request/response schemas
│   ├── services/               # Business logic layer
│   ├── core/                   # Core utilities (config, security, etc.)
│   ├── main.py                 # Application entry point
│   ├── init_db.py              # Database initialization script
│   ├── requirements.txt        # Python dependencies
│   └── .env.example            # Backend environment template
├── frontend/                   # Vue 3 frontend
│   ├── src/
│   │   ├── components/         # Reusable Vue components
│   │   ├── views/              # Page-level components
│   │   ├── stores/             # Pinia state stores
│   │   ├── api/                # API client layer
│   │   ├── router/             # Vue Router configuration
│   │   └── assets/             # Static assets
│   ├── package.json            # Node.js dependencies
│   └── vite.config.ts          # Vite configuration
├── data/                       # SQLite database (generated)
├── start.sh                    # Linux/macOS startup script
├── start.bat                   # Windows startup script
├── start.py                    # Cross-platform Python startup script
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── README_zh.md                # Chinese documentation
└── LICENSE                     # Apache 2.0 license
```

## API Documentation

When the backend is running, interactive API documentation is available at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite:///./data/app.db` |
| `JWT_SECRET` | Secret key for JWT signing | (required) |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRATION_HOURS` | JWT token expiration time | `168` |
| `ENCRYPTION_KEY` | Fernet key for data encryption | (required) |
| `DEFAULT_ADMIN_USERNAME` | Default admin username | `admin` |
| `DEFAULT_ADMIN_PASSWORD` | Default admin password | `admin123` |
| `DEFAULT_ADMIN_EMAIL` | Default admin email | `admin@example.com` |
| `HOST` | Server bind address | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `AGNES_API_BASE_URL` | Agnes AI API base URL | `https://apihub.agnes-ai.com/v1` |
| `AGNES_API_KEY` | Agnes AI API key | (required) |

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the project's coding standards and includes appropriate tests.

## License

This project is licensed under the Apache License 2.0 -- see the [LICENSE](LICENSE) file for details.

---

**Creative AI Platform** -- Empowering creativity through artificial intelligence.