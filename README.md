# 🧠 Innovation Tracker Backend (FastAPI)

This is the backend server for the **Innovation Tracker** web application. It is built using **FastAPI** and **SQLite** to manage innovative ideas, likes, and comments.

---

## 🚀 Features

- CRUD operations for Ideas
- Like toggling system (unique per user)
- Comments per idea
- CORS enabled to allow frontend interaction

---

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn
```

SQLite is used as the default database; no additional setup is needed.

---

## 🧪 Running the App

```bash
uvicorn main:app --reload
```

> By default the app runs on: `http://127.0.0.1:8000`

---

## 📦 API Endpoints

- `GET /ideas` – List all ideas (with comment count)
- `POST /ideas` – Create new idea
- `PUT /ideas/{id}` – Update idea
- `DELETE /ideas/{id}` – Delete idea
- `POST /ideas/{id}/like?user_id=...` – Toggle like (by user ID)
- `GET /ideas/{id}/comments` – Get all comments for idea
- `POST /comments` – Add comment

---

## 🧠 Notes

- Database file `ideas.db` will be auto-generated on first run
- Includes three tables: `ideas`, `comments`, and `likes`

---

## ☁️ Deployment (Heroku or others)

1. Use **gunicorn** or **uvicorn** for production
2. Set up `Procfile`, `requirements.txt`, and ensure SQLite is committed if needed
3. Use `GitHub Actions` or manual deployment