FROM python:3.12-slim

WORKDIR /app

# System deps voor pypdf / docx image extraction
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl \
    && rm -rf /var/lib/apt/lists/*

# Haal htmx op als statisch bestand (geen CDN-afhankelijkheid op runtime)
RUN curl -fsSL https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js \
    -o /tmp/htmx.min.js

# Anonimizer core installeren
RUN git clone --depth=1 https://github.com/security-commons-nl/anonimizer.git /anonimizer
RUN pip install --no-cache-dir -r /anonimizer/requirements.txt

# Web app installeren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# htmx in static map plaatsen
RUN cp /tmp/htmx.min.js /app/static/htmx.min.js

ENV ANONIMIZER_PATH=/anonimizer
ENV FLASK_APP=app.py
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "-m", "gunicorn", "app:app", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "1", \
     "--timeout", "300", \
     "--access-logfile", "-"]
