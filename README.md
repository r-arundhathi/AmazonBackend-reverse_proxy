### 🔀 Nginx Reverse Proxy Configuration

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://amazon-api:8000;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Explanation:**
- `listen 80` – Accepts HTTP requests on port 80.
- `server_name localhost` – Configures the server for local access.
- `location /` – Handles incoming requests.
- `proxy_pass` – Forwards requests to the FastAPI backend running on port 8000.
- `proxy_set_header` – Passes the original host, client IP, and protocol information to the backend.

**In short:** Nginx receives client requests and forwards them to the FastAPI backend through the Docker network.
