FROM python:3.14-slim

WORKDIR /app

# System deps voor pypdf / docx image extraction
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Anonimizer core installeren
RUN git clone --depth=1 https://github.com/security-commons-nl/anonimizer.git /anonimizer
RUN pip install --no-cache-dir -r /anonimizer/requirements.txt

# Web app installeren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV ANONIMIZER_PATH=/anonimizer
ENV FLASK_APP=app.py
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Least privilege: draai niet als root
RUN adduser --disabled-password --gecos '' app \
    && chown -R app:app /app
USER app

EXPOSE 5000

CMD ["python", "-m", "gunicorn", "app:app", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "1", \
     "--timeout", "300", \
     "--access-logfile", "-"]
