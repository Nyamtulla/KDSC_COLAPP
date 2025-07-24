

## 🚀 Project Pipeline Overview

### 1. Services and Where They Run
| Service         | Where to Run         | How to Start                        |
|-----------------|---------------------|-------------------------------------|
| PostgreSQL      | Windows (native)    | Start your local PostgreSQL service |
| Redis           | Docker (Linux)      | `docker run -d --name redis-server -p 6379:6379 redis:8.0.3` |
| Flask Backend   | Windows (native)    | `python app.py` (with correct env)  |
| RQ Worker       | Docker (Linux)      | See below                           |
| Ollama LLM      | Windows (native)    | Start Ollama as per its docs        |

---

### 2. Environment Variables

#### For Flask Backend (Windows)
```powershell
$env:SQLALCHEMY_DATABASE_URI="postgresql://postgres:colapp@localhost:5432/grocery_app_db"
python app.py
```

#### For RQ Worker (Docker)
Set these in your `docker run` command:
- `REDIS_URL=redis://host.docker.internal:6379/0`
- `SQLALCHEMY_DATABASE_URI=postgresql://postgres:colapp@host.docker.internal:5432/grocery_app_db`

---

### 3. Building and Running the RQ Worker in Docker

```sh
docker build -t colapp-rqworker .
docker run --rm -it --name colapp-rqworker \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  -e SQLALCHEMY_DATABASE_URI=postgresql://postgres:colapp@host.docker.internal:5432/grocery_app_db \
  -v %cd%:/app \
  colapp-rqworker
```

---

### 4. Ollama LLM Service

- Make sure Ollama is running on your Windows host and listening on port 11434.
- In your `offline_config.json`, set:
  ```json
  "host": "http://host.docker.internal:11434"
  ```
  This allows the RQ worker in Docker to access the LLM.

---

### 5. Frontend

- The frontend (if Flutter web or other) should point to your backend at `http://localhost:5000`.

---

### 6. Typical Startup Order

1. Start PostgreSQL (Windows)
2. Start Redis (Docker)
3. Start Ollama (Windows)
4. Start Flask backend (Windows, with correct env)
5. Build and run RQ worker (Docker)
6. Start frontend (if needed)

---

## 🏁 Single Command Quickstart

Open separate terminals for each service and run the following:

**Terminal 1: Start Redis (Docker)**
```sh
docker run -d --name redis-server -p 6379:6379 redis:8.0.3
```

**Terminal 2: Start Flask Backend (Windows, PowerShell)**
```powershell
$env:SQLALCHEMY_DATABASE_URI="postgresql://postgres:colapp@localhost:5432/grocery_app_db"
python app.py
```

**Terminal 3: Start RQ Worker (Docker, from backend directory)**
```sh
docker build -t colapp-rqworker .
docker run --rm -it --name colapp-rqworker \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  -e SQLALCHEMY_DATABASE_URI=postgresql://postgres:colapp@host.docker.internal:5432/grocery_app_db \
  -v %cd%:/app \
  colapp-rqworker
```

**Terminal 4: Start Ollama LLM (Windows)**
- Follow Ollama's documentation to start the service on port 11434.

**Terminal 5: Start Frontend (if needed)**
- Usual Flutter or web start command, making sure it points to `http://localhost:5000` for the backend.

---

### 🐳 Single-Line Docker Run for RQ Worker

If you want to run the RQ worker with a single command (no line breaks), use:

```sh
docker run --rm -it --name colapp-rqworker -e REDIS_URL=redis://host.docker.internal:6379/0 -e SQLALCHEMY_DATABASE_URI=postgresql://postgres:colapp@host.docker.internal:5432/grocery_app_db -v %cd%:/app colapp-rqworker
```

- Use this in Windows CMD or PowerShell for convenience.
- Make sure you are in the backend directory when running this command.

---

- Make sure Docker Desktop is running before starting Docker containers.
- If you update your code or dependencies, rebuild the RQ worker image.
- Use `host.docker.internal` for Docker-to-Windows communication. 

---

## 🛠 Troubleshooting: Multiple Redis Servers (HSET Error)

If you get HSET errors, you may have more than one Redis server running. To check and fix this on Windows:

**1. Check which processes are using port 6379:**
```sh
netstat -ano | findstr 6379
```

**2. Identify the programs using those PIDs:**
```sh
tasklist /FI "PID eq <PID>"
```
Replace `<PID>` with the number(s) you see from the previous command.

**3. Kill the unwanted Redis process (example for PID 5912):**
```sh
taskkill /PID 5912 /F
```

- Only your Docker Redis container should be running on port 6379.
- After killing the extra process, restart your RQ worker if needed. 

