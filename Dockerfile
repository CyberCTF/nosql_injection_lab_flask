FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY build/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY build/ .

# Expose the port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"] 

