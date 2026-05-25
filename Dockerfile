FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1\
    PYTHONDONTWRITEBYTECODE=1

ENV FLASK_ENV=production\
    PYTHONPATH=app.py

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY . .

RUN useradd -m appuser
USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0:8000", "app:app"]
