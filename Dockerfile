# Use Python 3.13 Alpine image
FROM python:3.13-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev \
    && apk add --no-cache jpeg-dev zlib-dev

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    FLASK_APP=wsgi:app \
    FLASK_ENV=production

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r requirements.txt

# Remove build dependencies
RUN apk del .build-deps

# Copy application code
COPY . .

# Create non-root user and switch to it
RUN adduser -D myuser && \
    chown -R myuser:myuser /app
USER myuser

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]
