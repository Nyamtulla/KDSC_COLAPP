# Colapp V3

## Getting Started (Dockerized Setup)

### 1. Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop) and Docker Compose installed
- (Optional) [Git](https://git-scm.com/) for cloning the repository

### 2. Clone the Repository
```sh
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 3. Build and Start All Services
```sh
docker-compose build
docker-compose up -d
```
- This will start the backend API, worker, Redis, Postgres, and Ollama containers.

### 4. Initialize the Database Schema
If your app does not auto-create tables, run:
```sh
docker-compose exec backend python init_db.py
```

### 5. Access the App
- **Backend API:** http://localhost:5000
- **Ollama (LLM):** http://localhost:11434
- **Postgres:** localhost:5432 (for DB tools)

### 6. Stopping the App
```sh
docker-compose down
```

### 7. Viewing Database Tables (Postgres)
#### Option 1: Using psql in Docker
```sh
docker-compose exec db bash
psql -U postgres -d grocery_app_db
```
- List tables: `\dt`
- View data: `SELECT * FROM receipts;`
- Exit: `\q`

#### Option 2: Using a GUI Tool
- Connect to `localhost:5432` with user `postgres`, password `colapp`, database `grocery_app_db`.

### 8. Cleaning Up Test/Invalid Receipts
To delete receipts with store name 'Processing...' or 'Unknown Store':
```sql
DELETE FROM receipt_items WHERE receipt_id IN (SELECT id FROM receipts WHERE store_name = 'Processing...' OR store_name = 'Unknown Store');
DELETE FROM receipts WHERE store_name = 'Processing...' OR store_name = 'Unknown Store';
```

### 9. Logs and Debugging
- View logs for a service:
  ```sh
  docker-compose logs backend
  docker-compose logs worker
  ```
- Watch all logs live:
  ```sh
  docker-compose logs -f
  ```

### 10. Frontend
- For development, run Flutter frontend natively:
  ```sh
  cd colapp/frontend
  flutter run -d chrome
  ```
- For production, see instructions to Dockerize the frontend.

---

## Notes
- Make sure to update environment variables and secrets for production.
- For deployment on a new server, repeat steps 1–6 above.

---

For further help, see the documentation or contact the maintainer. 