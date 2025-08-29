FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1 \
	POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# System deps for Pillow if needed later; keep minimal
RUN apt-get update -y && apt-get install -y --no-install-recommends \
	build-essential \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip wheel setuptools && pip install -r requirements.txt

COPY . .

# Create instance and uploads
RUN mkdir -p /app/instance /app/app/static/img/uploads

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "-b", "0.0.0.0:8000", "wsgi:app"]

