# Simple Dockerfile for containerizing the Email Priority Agent

FROM python:3.11-slim

# Set workdir inside the container
WORKDIR /app

# Copy dependency list and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose the port Flask will listen on INSIDE the container
EXPOSE 8000

# Use gunicorn to run the Flask app (app:app = app.py's 'app' object)
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]

