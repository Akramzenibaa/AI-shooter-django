# Deployment Guide (Contabo/Ubuntu VPS)

This guide helps you set up **PostgreSQL** and run your app on a VPS.

## 1. Install PostgreSQL
Run these commands on your VPS terminal:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
```

## 2. Create Database and User
Log into the Postgres shell:
```bash
sudo -u postgres psql
```

Run these SQL commands (replace `mypassword` with a secure password):
```sql
CREATE DATABASE ai_shooter;
CREATE USER ai_user WITH PASSWORD 'mypassword';
ALTER ROLE ai_user SET client_encoding TO 'utf8';
ALTER ROLE ai_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ai_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ai_shooter TO ai_user;
\q
```

## 3. Configure Your App
In your project folder on the VPS, create a `.env` file (`nano .env`) with:

```bash
# Security
DEBUG=False
SECRET_KEY=long-random-string-here
ALLOWED_HOSTS=your-domain.com

# Database (The URL matches the user/pass you just created)
DATABASE_URL=postgres://ai_user:mypassword@localhost:5432/ai_shooter

# AI API
GOOGLE_API_KEY=your-gemini-key

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=lbahidigital@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 4. Run the App
```bash
pip install -r requirements.txt
python manage.py collectstatic
python manage.py migrate
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```
