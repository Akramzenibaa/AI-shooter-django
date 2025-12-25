# Docker Deployment Guide (The Easiest Way)

This method automates **everything** (installing Postgres, connecting it, running the app).

## 1. Prepare Server
On your Contabo VPS, install Docker and Git:
```bash
sudo apt update
sudo apt install docker.io docker-compose git -y
```

## 2. Clone & Configure
Clone your repository:
```bash
git clone https://github.com/yourusername/ai-shooter.git
cd ai-shooter
```

Create `.env` file (`nano .env`) with **Docker-specific database settings**:
```bash
# Security
DEBUG=False
SECRET_KEY=replace-this-with-random-string
ALLOWED_HOSTS=your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com

# Database (Use the service name 'db' as the host)
DATABASE_URL=postgres://ai_user:mypassword@db:5432/ai_shooter

# AI API
GOOGLE_API_KEY=your-gemini-key
```

## 3. Launch
Run one command to start everything:
```bash
sudo docker-compose up -d --build
```
-   `-d`: Runs in background.
-   `--build`: Builds your code.

## 4. Final Setup (Once)
Run the migration inside the container:
```bash
sudo docker-compose exec web python manage.py migrate
sudo docker-compose exec web python manage.py collectstatic --noinput
```

That's it! access your site at `http://your-ip:8000` (or configure Nginx for domain).
