# Instagram-like Backend API

A RESTful backend API built with FastAPI that supports photo/video sharing with user authentication, feed, likes, and media uploads via ImageKit.

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy** (async) — ORM
- **SQLite** — database
- **fastapi-users** — authentication (JWT)
- **ImageKit** — media storage and CDN

## Features

- User registration and JWT authentication
- Upload photos and videos with captions
- Feed with chronological posts
- Like / unlike posts
- Delete your own posts

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/artnes717/Backend-project.git
cd Backend-project
```

### 2. Install dependencies
```bash
pip install uv
uv sync
```

### 3. Set up environment variables
Create a `.env` file in the root:
IMAGEKIT_PRIVATE_KEY=your_private_key
IMAGEKIT_PUBLIC_KEY=your_public_key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io/your_id
JWT_SECRET=your_secret_key

### 4. Run the server
```bash
uv run ./main.py
```

API docs available at `http://localhost:8000/docs`