FROM python:3.12.1
WORKDIR data_loader
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UVICORN_WORKERS=1

# Uvicorn settings
ENV PORT=8005
ENV HOST=0.0.0.0
ENV LOG_LEVEL=INFO
ENV WORKERS=1
ENV RELOAD="True"

# Application settings
ENV TITLE="Data Loader"
ENV DESCRIPTION="Data download service"
ENV VERSION="0.0.1"
ENV DOCS_URL="/docs"
ENV REDOC_URL="/redoc"
ENV OPENAPI_URL="/openapi.json"
ENV APP_HOST=${HOST}
ENV APP_PORT=${PORT}

# Settings logging
ENV LEVEL="INFO"
ENV GURU="True"
ENV TRACEBACK="false"

# Excel File settings
# 50Mb
ENV SIZE=524288000

# Yandex disk settings
ENV YA_TOKEN=NULL
ENV YA_CLIENT_ID=NULL
ENV YA_DIR="temp_folder"
ENV YA_ATTEMPT_COUNT=2

# Building
ENV UVICORN_ARGS "core.app:setup_app --host $APP_HOST --port $APP_PORT --workers $UVICORN_WORKERS"
RUN pip install --upgrade pip  --no-cache-dir
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY data_loader .

CMD uvicorn $UVICORN_ARGS