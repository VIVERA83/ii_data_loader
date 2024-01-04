FROM python:3.12.1
WORKDIR app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UVICORN_WORKERS=1

 # Setting base application
ENV APP_SECRET_KEY="secret-key"

# Settings for the crawler
ENV LOGIN_URL="http://localhost"
ENV VIEW_URL="http://localhost"
ENV COURSES=[1001,1023]

# Settings for PostgresSQL database connections
ENV POSTGRES_DB="test_db"
ENV POSTGRES_USER="test_user"
ENV POSTGRES_PASSWORD="test_password"
ENV POSTGRES_HOST="0.0.0.0"
ENV POSTGRES_PORT="5432"
ENV POSTGRES_SCHEMA="labor_project"

# Settings for Redis
ENV REDIS_DB="1"
ENV REDIS_HOST="0.0.0.0"
ENV REDIS_PORT="2541"
ENV REDIS_USER="default"
ENV REDIS_PASSWORD="test_password"

# Settings for authorization
ENV AUTH_KEY="auth-key"
ENV AUTH_ALGORITHMS="HS256"
ENV AUTH_ACCESS_EXPIRES_DELTA="360"
ENV AUTH_REFRESH_EXPIRES_DELTA="500"

# Setting Schedule
ENV LIMIT=5
ENV REFRESH_DELAY=4

# Building
ENV UVICORN_ARGS "core.app:app --host $APP_HOST --port $APP_PORT --workers $UVICORN_WORKERS"
RUN pip install --upgrade pip  --no-cache-dir
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app .

CMD uvicorn $UVICORN_ARGS